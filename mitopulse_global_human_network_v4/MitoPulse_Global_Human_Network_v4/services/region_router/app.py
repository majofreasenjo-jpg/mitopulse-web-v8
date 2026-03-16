from fastapi import FastAPI
import time

app = FastAPI(title="Region Router", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"region_router","ts":int(time.time())}

import requests

IDENTITY_URL = "http://identity_engine:8081"
GRAPH_URL = "http://trust_graph:8082"
POLICY_URL = "http://policy_engine:8084"
AUDIT_URL = "http://audit_ledger:8086"
LEDGER_URL = "http://ledger_service:8092"

@app.post("/route/presence")
def route_presence(body: dict):
    payload = body["payload"]
    policy = requests.post(f"{POLICY_URL}/policy/evaluate", json={
        "tenant_id": payload["tenant_id"],
        "stability": payload["stability"],
        "risk": payload["risk"],
        "human_conf": payload["human_conf"],
    }, timeout=10).json()
    identity = requests.post(f"{IDENTITY_URL}/identity/evaluate", json=payload, timeout=10).json()
    graph = requests.post(f"{GRAPH_URL}/graph/update", json={**payload, "identity_result": identity}, timeout=10).json()
    ledger = requests.post(f"{LEDGER_URL}/ledger/append", json={
        "event_type": "presence",
        "tenant_id": payload["tenant_id"],
        "user_id": payload["user_id"],
        "device_id": payload["device_id"],
        "region": body.get("region"),
        "policy": policy,
    }, timeout=10).json()
    requests.post(f"{AUDIT_URL}/audit/append", json={
        "action": "presence",
        "tenant_id": payload["tenant_id"],
        "user_id": payload["user_id"],
        "device_id": payload["device_id"],
        "region": body.get("region"),
        "policy": policy,
        "identity": identity,
    }, timeout=10)
    return {"policy": policy, "identity": identity, "graph": graph, "ledger": ledger}
