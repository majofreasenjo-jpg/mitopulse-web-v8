from fastapi import FastAPI
import time

app = FastAPI(title="Event Worker", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"event_worker","ts":int(time.time())}

@app.get("/worker/status")
def worker_status():
    return {"status":"idle","mode":"scaffold"}
