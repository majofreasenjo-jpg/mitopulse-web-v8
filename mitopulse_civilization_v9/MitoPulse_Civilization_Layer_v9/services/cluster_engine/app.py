from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse cluster_engine", version="9.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"cluster_engine","ts":int(time.time())}
