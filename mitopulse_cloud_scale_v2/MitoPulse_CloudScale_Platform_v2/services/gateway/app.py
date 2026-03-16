from fastapi import FastAPI
import time
app = FastAPI(title="MitoPulse Gateway", version="2.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"gateway","ts":int(time.time())}

from typing import Dict, Any
from fastapi import Header, HTTPException
from pydantic import BaseModel
import requests

IDENTITY_URL = "http://identity_engine:8081"
GRAPH_URL = "http://trust_graph:8082"
CONTINUITY_URL = "http://continuity_service:8083"
POLICY_URL = "http://policy_engine:8084"
AUDIT_URL = "http://audit_ledger:8086"
RECOVERY_URL = "http://recovery_service:8087"
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

@app.post("/v2/presence/event")
def presence_event(body: PresenceEvent, x_tenant_id: str | None = Header(default=None), idempotency_key: str | None = Header(default=None)):
    tenant = x_tenant_id or body.tenant_id
    if tenant != body.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_mismatch")
    if idempotency_key:
        if idempotency_key in IDEMPOTENCY:
            return {"ok": True, "idempotent": True}
        IDEMPOTENCY.add(idempotency_key)

    pol = requests.post(f"{POLICY_URL}/policy/evaluate", json={
        "tenant_id": body.tenant_id,
        "stability": body.stability,
        "risk": body.risk,
        "human_conf": body.human_conf,
    }, timeout=10).json()

    ident = requests.post(f"{IDENTITY_URL}/identity/evaluate", json=body.model_dump(), timeout=10).json()
    graph = requests.post(f"{GRAPH_URL}/graph/update", json={**body.model_dump(), "identity_result": ident}, timeout=10).json()
    requests.post(f"{AUDIT_URL}/audit/append", json={"action":"presence_event","tenant_id":body.tenant_id,"user_id":body.user_id,"device_id":body.device_id,"policy":pol,"identity":ident}, timeout=10)
    requests.post(f"{BILLING_URL}/meter/record", json={"tenant_id": body.tenant_id, "metric":"presence_event", "qty":1}, timeout=10)
    return {"ok": True, "policy": pol, "identity": ident, "graph": graph}

@app.get("/v2/identity/state")
def identity_state(tenant_id: str, user_id: str, device_id: str):
    return requests.get(f"{IDENTITY_URL}/identity/state", params={"tenant_id":tenant_id,"user_id":user_id,"device_id":device_id}, timeout=10).json()

@app.post("/v2/identity/continuity/start")
def continuity_start(payload: Dict[str, Any]):
    return requests.post(f"{CONTINUITY_URL}/continuity/start", json=payload, timeout=10).json()

@app.post("/v2/identity/continuity/complete")
def continuity_complete(payload: Dict[str, Any]):
    return requests.post(f"{CONTINUITY_URL}/continuity/complete", json=payload, timeout=10).json()

@app.post("/v2/identity/recovery/request")
def recovery_request(payload: Dict[str, Any]):
    return requests.post(f"{RECOVERY_URL}/recovery/request", json=payload, timeout=10).json()

@app.post("/v2/identity/recovery/approve")
def recovery_approve(payload: Dict[str, Any]):
    return requests.post(f"{RECOVERY_URL}/recovery/approve", json=payload, timeout=10).json()

@app.post("/v2/verify/group")
def verify_group(payload: Dict[str, Any]):
    pol = requests.post(f"{POLICY_URL}/policy/group_verify", json=payload, timeout=10).json()
    requests.post(f"{AUDIT_URL}/audit/append", json={"action":"group_verify","payload":payload,"result":pol}, timeout=10)
    requests.post(f"{BILLING_URL}/meter/record", json={"tenant_id": payload.get("tenant_id","unknown"), "metric":"group_verify", "qty":1}, timeout=10)
    return pol
