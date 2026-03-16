
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import random

app = FastAPI(title="MitoPulse v14 – Explainability Engine")

class EvalRequest(BaseModel):
    source_node_id: str
    target_node_id: str
    amount_anomaly: float = 0.5
    routine_break: float = 0.5
    shared_reality: float = 50
    guardian_score: float = 50
    fraud_exposure: float = 10

def explain_decision(rds, ass, srs, sc, fe):
    reasons = []

    if sc < 40:
        reasons.append("Strong behavioral anomaly detected")
    elif sc < 60:
        reasons.append("Moderate behavioral deviation")

    if srs < 30:
        reasons.append("Low shared reality between nodes")

    if ass < 40:
        reasons.append("Low trust / guardian score")

    if fe > 50:
        reasons.append("High fraud exposure propagated in graph")

    if not reasons:
        reasons.append("Interaction consistent with historical patterns")

    return reasons

@app.post("/evaluate")
def evaluate(req: EvalRequest):

    rds = random.randint(20,80)
    ass = int((req.guardian_score*0.6) + random.randint(0,20))
    srs = req.shared_reality
    sc = int(100 - ((req.amount_anomaly*100 + req.routine_break*100)/2))
    fe = req.fraud_exposure

    score = round((rds + ass + srs + sc)/4 - fe,2)

    if score >= 80:
        decision = "VERIFY"
    elif score >= 60:
        decision = "REVIEW"
    else:
        decision = "BLOCK"

    reasons = explain_decision(rds,ass,srs,sc,fe)

    return {
        "timestamp": datetime.utcnow(),
        "decision": decision,
        "trust_score": score,
        "explanation": {
            "relationship_depth_score": rds,
            "authority_score": ass,
            "shared_reality_score": srs,
            "behavior_score": sc,
            "fraud_exposure": fe,
            "reasons": reasons
        }
    }

@app.get("/health")
def health():
    return {"status":"MitoPulse v14 running"}
