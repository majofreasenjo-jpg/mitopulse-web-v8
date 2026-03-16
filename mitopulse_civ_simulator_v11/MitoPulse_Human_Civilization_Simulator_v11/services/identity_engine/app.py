from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse identity_engine", version="11.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"identity_engine","ts":int(time.time())}
