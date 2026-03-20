from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse audit_ledger", version="3.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"audit_ledger","ts":int(time.time())}
