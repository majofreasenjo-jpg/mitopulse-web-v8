from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse civilization_engine", version="11.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"civilization_engine","ts":int(time.time())}
