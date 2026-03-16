from fastapi import FastAPI
import time
app = FastAPI(title="Verify Api", version="1.0.0")
@app.get("/health")
def health():
    return {"status":"ok","service":"verify_api","ts":int(time.time())}
@app.post("/verify/presence")
def verify(body: dict):
    return {"mode":"hardening_core_scaffold","received":body}
