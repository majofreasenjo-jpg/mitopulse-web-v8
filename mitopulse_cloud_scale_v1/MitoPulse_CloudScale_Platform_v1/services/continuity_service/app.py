from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import time

app = FastAPI(title="MitoPulse Continuity Service", version="1.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"continuity_service","ts":int(time.time())}

TOKENS = {}

class ContinuityStart(BaseModel):
    tenant_id: str
    user_id: str
    old_device_id: str
    new_device_id: str

class ContinuityComplete(BaseModel):
    tenant_id: str
    user_id: str
    old_device_id: str
    new_device_id: str
    token: str

@app.post("/continuity/start")
def continuity_start(body: ContinuityStart):
    token = f"{body.tenant_id}|{body.user_id}|{body.old_device_id}|{body.new_device_id}|{int(time.time())}"
    TOKENS[token] = body.model_dump()
    return {"token": token, "ok": True}

@app.post("/continuity/complete")
def continuity_complete(body: ContinuityComplete):
    if body.token not in TOKENS:
        return {"ok": False, "reason": "invalid_token"}
    return {"ok": True, "new_epoch": 2}
