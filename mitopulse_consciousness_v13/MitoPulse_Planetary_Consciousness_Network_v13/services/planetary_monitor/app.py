from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse planetary_monitor", version="13.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"planetary_monitor","ts":int(time.time())}
