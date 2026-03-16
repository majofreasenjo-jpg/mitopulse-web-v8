from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse identity_engine", version="8.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"identity_engine","ts":int(time.time())}
