
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import random

app = FastAPI(title="MitoPulse v16 – Trust Propagation Engine")

# Simple in‑memory trust graph
graph = {
    "nd_manu_01": {"nd_ana_01": 0.8, "nd_bruno_01": 0.7},
    "nd_ana_01": {"nd_manu_01": 0.8, "nd_carla_01": 0.6},
    "nd_bruno_01": {"nd_manu_01": 0.7},
    "nd_carla_01": {"nd_ana_01": 0.6}
}

fraud_risk = {
    "nd_manu_01": 10,
    "nd_ana_01": 10,
    "nd_bruno_01": 10,
    "nd_carla_01": 10
}

class PropagationRequest(BaseModel):
    infected_node: str
    initial_risk: float = 70
    decay: float = 0.6

def propagate(node, risk, decay, visited):
    if node in visited:
        return
    visited.add(node)

    fraud_risk[node] = max(fraud_risk[node], risk)

    neighbors = graph.get(node, {})
    for neighbor, trust in neighbors.items():
        propagated_risk = risk * trust * decay
        if propagated_risk > 5:
            propagate(neighbor, propagated_risk, decay, visited)

@app.post("/propagate")
def propagate_risk(req: PropagationRequest):

    visited = set()
    propagate(req.infected_node, req.initial_risk, req.decay, visited)

    return {
        "timestamp": datetime.utcnow(),
        "infected_node": req.infected_node,
        "affected_nodes": list(visited),
        "risk_map": fraud_risk
    }

@app.get("/graph")
def get_graph():
    return graph

@app.get("/risk")
def get_risk():
    return fraud_risk

@app.get("/health")
def health():
    return {"status":"MitoPulse v16 Trust Propagation running"}
