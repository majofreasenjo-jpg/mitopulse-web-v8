from fastapi import FastAPI
import time

app = FastAPI(title="Policy Engine", version="4.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"policy_engine","ts":int(time.time())}

@app.post("/policy/evaluate")
def policy_evaluate(body: dict):
    verdict = "ok"
    if body.get("risk", 0) > 80 or body.get("human_conf", 0) < 0.7:
        verdict = "fail"
    elif body.get("stability", 1) < 0.45:
        verdict = "suspicious"
    return {"verdict": verdict, "tenant_id": body.get("tenant_id")}

@app.post("/policy/group_verify")
def group_verify(body: dict):
    members = body.get("members", [])
    q = body.get("require_quorum", 2)
    return {"ok": len(members) >= q, "accepted": members[:q], "rejected": members[q:], "require_quorum": q}
