from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse developer_portal", version="8.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"developer_portal","ts":int(time.time())}
