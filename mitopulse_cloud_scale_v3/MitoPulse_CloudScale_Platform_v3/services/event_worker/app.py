from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse event_worker", version="3.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"event_worker","ts":int(time.time())}
