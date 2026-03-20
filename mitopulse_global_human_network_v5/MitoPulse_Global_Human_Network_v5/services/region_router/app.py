from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse region_router", version="5.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"region_router","ts":int(time.time())}
