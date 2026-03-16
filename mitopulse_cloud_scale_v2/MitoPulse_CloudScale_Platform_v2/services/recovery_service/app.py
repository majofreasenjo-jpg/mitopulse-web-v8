from fastapi import FastAPI
import time
app = FastAPI(title="MitoPulse Recovery Service", version="2.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"recovery_service","ts":int(time.time())}

from pydantic import BaseModel
from typing import List
REQUESTS = {}

class RecoveryRequest(BaseModel):
    tenant_id: str
    user_id: str
    target_device_id: str
    approvers: List[str]

class RecoveryApprove(BaseModel):
    recovery_id: str
    approver_device_id: str

@app.post("/recovery/request")
def recovery_request(body: RecoveryRequest):
    rid = f"rec-{int(time.time()*1000)}"
    REQUESTS[rid] = {"tenant_id": body.tenant_id, "user_id": body.user_id, "target_device_id": body.target_device_id, "approvers": body.approvers, "approved_by": [], "status":"pending"}
    return {"recovery_id": rid, "status":"pending"}

@app.post("/recovery/approve")
def recovery_approve(body: RecoveryApprove):
    rr = REQUESTS.get(body.recovery_id)
    if not rr:
        return {"ok": False, "reason":"not_found"}
    if body.approver_device_id not in rr["approvers"]:
        return {"ok": False, "reason":"not_allowed"}
    if body.approver_device_id not in rr["approved_by"]:
        rr["approved_by"].append(body.approver_device_id)
    if len(rr["approved_by"]) >= 2:
        rr["status"] = "approved"
    return rr
