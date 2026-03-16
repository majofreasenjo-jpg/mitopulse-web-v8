from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import time

app = FastAPI(title="MitoPulse Identity Engine", version="1.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"identity_engine","ts":int(time.time())}

STATE = {}

class IdentityEval(BaseModel):
    tenant_id: str
    user_id: str
    device_id: str
    epoch: int
    tier: str
    index: float
    stability: float
    human_conf: float
    risk: int
    coercion: bool
    context: Dict[str, Any] = {}

def band(stability: float) -> str:
    if stability >= 0.75: return "stable"
    if stability >= 0.45: return "drift"
    return "anomaly"

@app.post("/identity/evaluate")
def identity_evaluate(body: IdentityEval):
    key = (body.tenant_id, body.user_id, body.device_id)
    STATE[key] = {
        "tenant_id": body.tenant_id,
        "user_id": body.user_id,
        "device_id": body.device_id,
        "epoch": body.epoch,
        "tier": body.tier,
        "index": body.index,
        "stability": body.stability,
        "stability_band": band(body.stability),
        "human_conf": body.human_conf,
        "risk": body.risk,
        "coercion": body.coercion,
        "context": body.context,
        "last_seen": int(time.time()),
    }
    return {"status":"ok","state":STATE[key]}

@app.get("/identity/state")
def identity_state(tenant_id: str, user_id: str, device_id: str):
    key = (tenant_id, user_id, device_id)
    if key not in STATE:
        return {"error":"no_state"}
    return STATE[key]
