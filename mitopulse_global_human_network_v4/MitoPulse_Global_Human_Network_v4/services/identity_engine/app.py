from fastapi import FastAPI
import time

app = FastAPI(title="Identity Engine", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"identity_engine","ts":int(time.time())}

from pydantic import BaseModel
from typing import Dict, Any
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

def band(x: float) -> str:
    if x >= 0.75: return "stable"
    if x >= 0.45: return "drift"
    return "anomaly"

@app.post("/identity/evaluate")
def evaluate(body: IdentityEval):
    STATE[(body.tenant_id, body.user_id, body.device_id)] = {
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
    return {"ok": True, "state": STATE[(body.tenant_id, body.user_id, body.device_id)]}

@app.get("/identity/state")
def state(tenant_id: str, user_id: str, device_id: str):
    return STATE.get((tenant_id, user_id, device_id), {"error":"no_state"})
