from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse continuity_service", version="5.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"continuity_service","ts":int(time.time())}
