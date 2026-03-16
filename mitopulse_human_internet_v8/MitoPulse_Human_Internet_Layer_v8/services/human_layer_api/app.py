from fastapi import FastAPI
import time

app = FastAPI(title="MitoPulse human_layer_api", version="8.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"human_layer_api","ts":int(time.time())}
