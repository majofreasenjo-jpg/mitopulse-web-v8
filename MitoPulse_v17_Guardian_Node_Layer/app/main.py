
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="MitoPulse v17 – Guardian Node Layer")

graph = {
    "nd_manu_01": {"nd_ana_01": 0.8, "nd_bruno_01": 0.7},
    "nd_ana_01": {"nd_manu_01": 0.8, "nd_carla_01": 0.6},
    "nd_bruno_01": {"nd_manu_01": 0.7, "guardian_bank_01": 0.9},
    "nd_carla_01": {"nd_ana_01": 0.6, "guardian_bank_01": 0.8},
    "guardian_bank_01": {"nd_bruno_01": 0.9, "nd_carla_01": 0.8, "guardian_telco_01": 0.85},
    "guardian_telco_01": {"guardian_bank_01": 0.85}
}

node_types = {
    "nd_manu_01": "pilot_user",
    "nd_ana_01": "pilot_user",
    "nd_bruno_01": "pilot_user",
    "nd_carla_01": "pilot_user",
    "guardian_bank_01": "guardian",
    "guardian_telco_01": "guardian",
}

guardian_policies = {
    "guardian_bank_01": {
        "name": "Bank Guardian",
        "block_threshold": 70,
        "review_threshold": 45,
        "sector": "banking"
    },
    "guardian_telco_01": {
        "name": "Telecom Guardian",
        "block_threshold": 75,
        "review_threshold": 50,
        "sector": "telecom"
    }
}

risk_map = {k: 10.0 for k in graph.keys()}

class GuardianEvalRequest(BaseModel):
    source_node: str
    target_node: str
    risk_score: float
    route: list[str] = []

class PropagationRequest(BaseModel):
    infected_node: str
    initial_risk: float = 80
    decay: float = 0.6

def propagate(node: str, risk: float, decay: float, visited: set[str]):
    if node in visited:
        return
    visited.add(node)
    risk_map[node] = max(risk_map[node], round(risk, 2))
    for neighbor, trust in graph.get(node, {}).items():
        next_risk = risk * trust * decay
        if next_risk > 5:
            propagate(neighbor, next_risk, decay, visited)

def guardian_decision(guardian_id: str, risk_score: float):
    policy = guardian_policies[guardian_id]
    if risk_score >= policy["block_threshold"]:
        return "BLOCK"
    if risk_score >= policy["review_threshold"]:
        return "REVIEW"
    return "ALLOW"

@app.get("/graph")
def get_graph():
    return {"graph": graph, "node_types": node_types}

@app.get("/guardians")
def get_guardians():
    return guardian_policies

@app.get("/risk")
def get_risk():
    return risk_map

@app.post("/propagate")
def propagate_risk(req: PropagationRequest):
    visited = set()
    propagate(req.infected_node, req.initial_risk, req.decay, visited)
    affected_guardians = [n for n in visited if node_types.get(n) == "guardian"]
    return {
        "timestamp": datetime.utcnow(),
        "infected_node": req.infected_node,
        "affected_nodes": list(visited),
        "affected_guardians": affected_guardians,
        "risk_map": risk_map
    }

@app.post("/guardian/evaluate")
def evaluate_by_guardians(req: GuardianEvalRequest):
    guardians_seen = [n for n in graph.keys() if node_types.get(n) == "guardian" and (n in graph.get(req.source_node, {}) or n in graph.get(req.target_node, {}) or n in req.route)]
    decisions = []
    final = "ALLOW"
    for gid in guardians_seen:
        d = guardian_decision(gid, req.risk_score)
        decisions.append({
            "guardian_id": gid,
            "guardian_name": guardian_policies[gid]["name"],
            "decision": d,
            "sector": guardian_policies[gid]["sector"]
        })
        if d == "BLOCK":
            final = "BLOCK"
        elif d == "REVIEW" and final != "BLOCK":
            final = "REVIEW"
    return {
        "timestamp": datetime.utcnow(),
        "source_node": req.source_node,
        "target_node": req.target_node,
        "risk_score": req.risk_score,
        "guardian_path": guardians_seen,
        "guardian_decisions": decisions,
        "final_decision": final
    }

@app.get("/health")
def health():
    return {"status": "MitoPulse v17 Guardian Node Layer running"}
