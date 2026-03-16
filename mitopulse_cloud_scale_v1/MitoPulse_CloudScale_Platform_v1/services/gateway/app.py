from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import time

app = FastAPI(title="MitoPulse Gateway", version="1.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"gateway","ts":int(time.time())}

import requests
from fastapi import HTTPException

IDENTITY_URL = "http://identity_engine:8081"
GRAPH_URL = "http://trust_graph:8082"
CONTINUITY_URL = "http://continuity_service:8083"
POLICY_URL = "http://policy_engine:8084"
AUDIT_URL = "http://audit_ledger:8086"

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

@app.post("/v1/presence/event")
def presence_event(body: PresenceEvent):
    # policy
    pol = requests.post(f"{POLICY_URL}/policy/evaluate", json={
        "tenant_id": body.tenant_id,
        "stability": body.stability,
        "risk": body.risk,
        "human_conf": body.human_conf,
    }, timeout=10).json()

    # identity
    ident = requests.post(f"{IDENTITY_URL}/identity/evaluate", json=body.model_dump(), timeout=10).json()

    # graph update
    graph = requests.post(f"{GRAPH_URL}/graph/update", json={
        **body.model_dump(),
        "identity_result": ident
    }, timeout=10).json()

    # audit
    requests.post(f"{AUDIT_URL}/audit/append", json={
        "action":"presence_event",
        "tenant_id": body.tenant_id,
        "user_id": body.user_id,
        "device_id": body.device_id,
        "result": ident,
        "policy": pol,
    }, timeout=10)

    return {"ok": True, "policy": pol, "identity": ident, "graph": graph}

@app.get("/v1/identity/state")
def identity_state(tenant_id: str, user_id: str, device_id: str):
    r = requests.get(f"{IDENTITY_URL}/identity/state", params={
        "tenant_id": tenant_id,
        "user_id": user_id,
        "device_id": device_id,
    }, timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()

@app.post("/v1/identity/continuity/start")
def continuity_start(payload: Dict[str, Any]):
    return requests.post(f"{CONTINUITY_URL}/continuity/start", json=payload, timeout=10).json()

@app.post("/v1/identity/continuity/complete")
def continuity_complete(payload: Dict[str, Any]):
    return requests.post(f"{CONTINUITY_URL}/continuity/complete", json=payload, timeout=10).json()

@app.post("/v1/verify/group")
def verify_group(payload: Dict[str, Any]):
    # group policy evaluated in policy service
    pol = requests.post(f"{POLICY_URL}/policy/group_verify", json=payload, timeout=10).json()
    requests.post(f"{AUDIT_URL}/audit/append", json={
        "action":"group_verify",
        "payload": payload,
        "result": pol,
    }, timeout=10)
    return pol
