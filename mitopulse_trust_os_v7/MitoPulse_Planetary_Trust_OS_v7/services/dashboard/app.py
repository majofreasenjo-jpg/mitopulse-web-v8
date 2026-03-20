from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse dashboard", version="7.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"dashboard","ts":int(time.time())}
