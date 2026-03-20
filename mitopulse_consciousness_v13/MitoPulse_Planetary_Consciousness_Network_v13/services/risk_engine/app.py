from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse risk_engine", version="13.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"risk_engine","ts":int(time.time())}
