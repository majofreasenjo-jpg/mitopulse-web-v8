from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse civilization_simulator", version="12.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"civilization_simulator","ts":int(time.time())}
