from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import time

app = FastAPI(title="MitoPulse Audit Ledger", version="1.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"audit_ledger","ts":int(time.time())}

LEDGER = []

@app.post("/audit/append")
def audit_append(payload: Dict[str, Any]):
    entry = {"ts": int(time.time()), **payload}
    LEDGER.append(entry)
    return {"ok": True, "size": len(LEDGER)}

@app.get("/audit/list")
def audit_list():
    return {"entries": LEDGER[-200:]}
