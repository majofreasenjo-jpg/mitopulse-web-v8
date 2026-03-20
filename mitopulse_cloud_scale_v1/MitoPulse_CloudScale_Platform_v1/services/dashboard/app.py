from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import time

app = FastAPI(title="MitoPulse Dashboard API", version="1.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"dashboard","ts":int(time.time())}

import requests

GATEWAY_URL = "http://gateway:8080"
GRAPH_URL = "http://trust_graph:8082"
AUDIT_URL = "http://audit_ledger:8086"

@app.get("/dashboard/summary")
def dashboard_summary():
    edges = requests.get(f"{GRAPH_URL}/graph/edges", timeout=10).json()
    audits = requests.get(f"{AUDIT_URL}/audit/list", timeout=10).json()
    return {
        "edges_count": len(edges.get("edges", [])),
        "audit_count": len(audits.get("entries", [])),
        "status": "ok"
    }
