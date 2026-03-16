from fastapi import FastAPI
import time

app = FastAPI(title="Recovery Service", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"recovery_service","ts":int(time.time())}

REQUESTS = {}

@app.post("/recovery/request")
def request_recovery(body: dict):
    rid = f"rec-{int(time.time()*1000)}"
    REQUESTS[rid] = {**body, "approved_by": [], "status":"pending"}
    return {"recovery_id": rid, "status":"pending"}

@app.post("/recovery/approve")
def approve_recovery(body: dict):
    rr = REQUESTS.get(body.get("recovery_id"))
    if not rr:
        return {"ok": False, "reason":"not_found"}
    approver = body.get("approver_device_id")
    allowed = rr.get("approvers", [])
    if approver not in allowed:
        return {"ok": False, "reason":"not_allowed"}
    if approver not in rr["approved_by"]:
        rr["approved_by"].append(approver)
    if len(rr["approved_by"]) >= 2:
        rr["status"] = "approved"
    return rr
