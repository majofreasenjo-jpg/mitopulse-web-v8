from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse policy_engine", version="3.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"policy_engine","ts":int(time.time())}
