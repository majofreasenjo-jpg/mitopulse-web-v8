from fastapi import FastAPI
app = FastAPI(title="Fraud Memory")
@app.get("/health")
def health(): return {"status":"ok","service":"fraud_memory"}
@app.post("/score")
def score(payload: dict):
    action = payload.get("action","")
    penalty = 0.03
    if action == "withdrawal": penalty += 0.04
    if payload.get("risk_score",0) > 0.45: penalty += 0.08
    if payload.get("baseline_penalty",0) > 0.15: penalty += 0.05
    return {"fraud_memory_penalty": round(max(0,min(penalty,1)),4)}
