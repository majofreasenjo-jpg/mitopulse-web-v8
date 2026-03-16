from fastapi import FastAPI
import time

app = FastAPI(title="Continuity Service", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"continuity_service","ts":int(time.time())}

TOKENS = {}

@app.post("/continuity/start")
def start(body: dict):
    token = f"{body['tenant_id']}|{body['user_id']}|{body['old_device_id']}|{body['new_device_id']}|{int(time.time())}"
    TOKENS[token] = body
    return {"ok": True, "token": token}

@app.post("/continuity/complete")
def complete(body: dict):
    if body["token"] not in TOKENS:
        return {"ok": False, "reason":"invalid_token"}
    return {"ok": True, "new_epoch": 2}
