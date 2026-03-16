from fastapi import FastAPI
import time
app = FastAPI(title="MitoPulse Dashboard API", version="2.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"dashboard","ts":int(time.time())}

import requests
GRAPH_URL = "http://trust_graph:8082"
AUDIT_URL = "http://audit_ledger:8086"

@app.get("/dashboard/summary")
def dashboard_summary():
    edges = requests.get(f"{GRAPH_URL}/graph/edges", timeout=10).json().get("edges", [])
    audits = requests.get(f"{AUDIT_URL}/audit/list", timeout=10).json().get("entries", [])
    return {"status":"ok","edges_count":len(edges),"audit_count":len(audits)}
