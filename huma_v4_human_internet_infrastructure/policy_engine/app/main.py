from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI(title="Policy Engine")
POLICIES = {
    "login": {"ok": 0.72, "review": 0.50},
    "account_creation": {"ok": 0.76, "review": 0.52},
    "checkout": {"ok": 0.78, "review": 0.55},
    "withdrawal": {"ok": 0.82, "review": 0.60},
}
class PolicyUpdate(BaseModel):
    action: str
    ok: float
    review: float
@app.get("/health")
def health(): return {"status":"ok","service":"policy_engine"}
@app.get("/policies")
def get_policies(): return {"policies": POLICIES}
@app.post("/policies")
def upsert_policy(body: PolicyUpdate):
    POLICIES[body.action] = {"ok": body.ok, "review": body.review}
    return {"status":"saved","action":body.action,"policy":POLICIES[body.action]}
@app.post("/evaluate")
def evaluate(payload: dict):
    action = payload.get("action","login")
    score = payload.get("global_human_score",0)
    policy = POLICIES.get(action, {"ok":0.78,"review":0.52})
    decision = "OK" if score >= policy["ok"] else "REVIEW" if score >= policy["review"] else "BLOCK"
    return {"decision": decision, "policy": policy}
