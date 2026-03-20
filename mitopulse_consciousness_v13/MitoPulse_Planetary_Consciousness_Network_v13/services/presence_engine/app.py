from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse presence_engine", version="13.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"presence_engine","ts":int(time.time())}
