from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse ledger_service", version="6.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"ledger_service","ts":int(time.time())}
