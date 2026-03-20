from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse recovery_service", version="5.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"recovery_service","ts":int(time.time())}
