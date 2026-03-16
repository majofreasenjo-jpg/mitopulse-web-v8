from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse billing_meter", version="5.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"billing_meter","ts":int(time.time())}
