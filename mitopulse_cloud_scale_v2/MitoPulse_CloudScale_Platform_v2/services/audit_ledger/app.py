from fastapi import FastAPI
import time
app = FastAPI(title="MitoPulse Audit Ledger", version="2.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"audit_ledger","ts":int(time.time())}

from typing import Dict, Any
LEDGER = []

@app.post("/audit/append")
def audit_append(payload: Dict[str, Any]):
    LEDGER.append({"ts": int(time.time()), **payload})
    return {"ok": True, "size": len(LEDGER)}

@app.get("/audit/list")
def audit_list():
    return {"entries": LEDGER[-200:]}
