from fastapi import FastAPI
import time
app = FastAPI(title="Gateway", version="1.0.0")
@app.get("/health")
def health():
    return {"status":"ok","service":"gateway","ts":int(time.time())}
@app.post("/v1/verify/presence")
def verify(body: dict):
    return {"gateway":"ok","payload":body}
