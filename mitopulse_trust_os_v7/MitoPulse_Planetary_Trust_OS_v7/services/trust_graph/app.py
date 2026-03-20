from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse trust_graph", version="7.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"trust_graph","ts":int(time.time())}
