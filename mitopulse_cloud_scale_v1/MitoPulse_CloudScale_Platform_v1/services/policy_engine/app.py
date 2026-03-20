from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import time

app = FastAPI(title="MitoPulse Policy Engine", version="1.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"policy_engine","ts":int(time.time())}

class PolicyEval(BaseModel):
    tenant_id: str
    stability: float
    risk: int
    human_conf: float

@app.post("/policy/evaluate")
def policy_evaluate(body: PolicyEval):
    verdict = "ok"
    if body.risk > 80 or body.human_conf < 0.7:
        verdict = "fail"
    elif body.stability < 0.45:
        verdict = "suspicious"
    return {"verdict": verdict, "tenant_id": body.tenant_id}

@app.post("/policy/group_verify")
def group_verify(payload: Dict[str, Any]):
    require_quorum = payload.get("require_quorum", 2)
    members = payload.get("members", [])
    # demo implementation
    accepted = members[:require_quorum]
    rejected = members[require_quorum:]
    return {"ok": len(accepted) >= require_quorum, "accepted": accepted, "rejected": rejected, "require_quorum": require_quorum}
