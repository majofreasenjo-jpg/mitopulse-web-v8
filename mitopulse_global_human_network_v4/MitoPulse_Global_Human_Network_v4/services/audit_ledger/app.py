from fastapi import FastAPI
import time

app = FastAPI(title="Audit Ledger", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"audit_ledger","ts":int(time.time())}

LEDGER = []

@app.post("/audit/append")
def append(body: dict):
    entry = {"ts": int(time.time()), **body}
    LEDGER.append(entry)
    return {"ok": True, "size": len(LEDGER)}

@app.get("/audit/list")
def list_entries():
    return {"entries": LEDGER[-200:]}
