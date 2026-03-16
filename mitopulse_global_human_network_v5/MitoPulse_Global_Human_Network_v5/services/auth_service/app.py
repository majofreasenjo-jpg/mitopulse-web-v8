from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse auth_service", version="5.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"auth_service","ts":int(time.time())}
