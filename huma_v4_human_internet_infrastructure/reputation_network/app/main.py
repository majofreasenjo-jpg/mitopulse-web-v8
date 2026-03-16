from fastapi import FastAPI
app = FastAPI(title="Reputation Network")
REPUTATION = {}
@app.get("/health")
def health(): return {"status":"ok","service":"reputation_network"}
@app.get("/score/{tenant_id}/{user_ref}")
def get_score(tenant_id: str, user_ref: str):
    score = REPUTATION.get((tenant_id, user_ref), 0.2)
    return {"tenant_id": tenant_id, "user_ref": user_ref, "reputation_score": score}
@app.post("/update")
def update(payload: dict):
    tenant_id = payload["tenant_id"]
    user_ref = payload["user_ref"]
    current = REPUTATION.get((tenant_id, user_ref), 0.2)
    session_score = float(payload.get("session_score", 0.2))
    new_score = round(max(0,min((current * 0.9) + (session_score * 0.1), 1.0)),4)
    REPUTATION[(tenant_id, user_ref)] = new_score
    return {"tenant_id": tenant_id, "user_ref": user_ref, "reputation_score": new_score}
