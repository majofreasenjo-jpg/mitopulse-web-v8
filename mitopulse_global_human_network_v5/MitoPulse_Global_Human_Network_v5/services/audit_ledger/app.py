from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse audit_ledger", version="5.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"audit_ledger","ts":int(time.time())}
