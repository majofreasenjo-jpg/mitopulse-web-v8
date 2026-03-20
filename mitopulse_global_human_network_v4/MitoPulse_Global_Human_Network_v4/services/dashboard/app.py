from fastapi import FastAPI
import time

app = FastAPI(title="Dashboard", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"dashboard","ts":int(time.time())}

import requests
GRAPH_URL = "http://trust_graph:8082"
AUDIT_URL = "http://audit_ledger:8086"
BILLING_URL = "http://billing_meter:8088"
LEDGER_URL = "http://ledger_service:8092"

@app.get("/dashboard/summary")
def summary():
    edges = requests.get(f"{GRAPH_URL}/graph/edges", timeout=10).json().get("edges", [])
    audits = requests.get(f"{AUDIT_URL}/audit/list", timeout=10).json().get("entries", [])
    billing = requests.get(f"{BILLING_URL}/meter/summary", timeout=10).json().get("usage", [])
    ledger = requests.get(f"{LEDGER_URL}/ledger/list", timeout=10).json().get("entries", [])
    return {"status":"ok","edges_count":len(edges),"audit_count":len(audits),"usage_count":len(billing),"ledger_count":len(ledger)}
