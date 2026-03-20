from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse Gateway", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"gateway","ts":int(time.time())}

from fastapi import Header, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import requests

AUTH_URL = "http://auth_service:8089"
ROUTER_URL = "http://region_router:8091"
BILLING_URL = "http://billing_meter:8088"

IDEMPOTENCY = set()

class PresenceEvent(BaseModel):
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

@app.get("/v4/healthcheck")
def healthcheck():
    return {"status":"gateway_ok","version":"v4"}

@app.post("/v4/presence")
def presence(payload: PresenceEvent, x_api_key: str | None = Header(default=None), x_region: str | None = Header(default="latam-south"), idempotency_key: str | None = Header(default=None)):
    auth = requests.post(f"{AUTH_URL}/auth/verify", json={"api_key": x_api_key, "tenant_id": payload.tenant_id}, timeout=10).json()
    if not auth.get("ok"):
        raise HTTPException(status_code=401, detail="unauthorized")
    if idempotency_key:
        if idempotency_key in IDEMPOTENCY:
            return {"ok": True, "idempotent": True}
        IDEMPOTENCY.add(idempotency_key)

    routed = requests.post(f"{ROUTER_URL}/route/presence", json={"region": x_region, "payload": payload.model_dump()}, timeout=15).json()
    requests.post(f"{BILLING_URL}/meter/record", json={"tenant_id": payload.tenant_id, "metric": "presence_v4", "qty": 1}, timeout=10)
    return {"ok": True, "region": x_region, "result": routed}
