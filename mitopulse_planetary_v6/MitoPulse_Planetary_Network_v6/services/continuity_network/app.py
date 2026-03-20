from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse continuity_network", version="6.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"continuity_network","ts":int(time.time())}
