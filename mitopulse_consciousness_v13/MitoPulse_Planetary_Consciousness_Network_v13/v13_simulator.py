from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="MitoPulse v13.1 Geospatial Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Event(BaseModel):
    user_id: str
    stability: float
    human_conf: float
    risk: int
    region: Optional[str] = "Global"

# Regional baseline data mapping
REGIONS = {
    "New York": {"stability": 0.92, "risk": 1, "presence": 4500},
    "London": {"stability": 0.88, "risk": 2, "presence": 3200},
    "Tokyo": {"stability": 0.42, "risk": 7, "presence": 5800}, # Anomaly hotspot for demo
    "São Paulo": {"stability": 0.95, "risk": 1, "presence": 2100},
    "Sydney": {"stability": 0.90, "risk": 1, "presence": 1500}
}

@app.get("/health")
def health():
    return {"status": "ok", "series": "v13.1", "ts": int(time.time())}

@app.post("/v13/signal")
def gateway_signal(e: Event):
    region_data = REGIONS.get(e.region, {"stability": e.stability, "risk": e.risk, "presence": 1200})
    
    stability = region_data["stability"]
    state = "stable" if stability >= 0.5 else "collective_anomaly"
    
    return {
        "region": e.region,
        "presence": {"status": "active", "count": region_data["presence"]},
        "risk": {"risk_level": "low" if region_data["risk"] < 5 else "high", "verdict": "pass"},
        "ai_detection": {"is_bot": False, "confidence": 0.99},
        "collective_state": {"collective_state": state, "node": e.user_id}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
