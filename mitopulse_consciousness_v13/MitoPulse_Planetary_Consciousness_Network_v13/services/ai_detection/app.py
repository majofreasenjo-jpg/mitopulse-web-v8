from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse ai_detection", version="13.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"ai_detection","ts":int(time.time())}
