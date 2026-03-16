from fastapi import FastAPI
import time
app = FastAPI(title="MitoPulse Trust Graph", version="2.0.0")

@app.get("/health")
def health():
    return {"status":"ok","service":"trust_graph","ts":int(time.time())}

from pydantic import BaseModel
from typing import Dict, Any
EDGES = []

class GraphUpdate(BaseModel):
    tenant_id: str
    user_id: str
    device_id: str
    epoch: int
    tier: str
    index: float
    stability: float
    human_conf: float
    risk: int
    coercion: bool
    context: Dict[str, Any] = {}
    identity_result: Dict[str, Any]

@app.post("/graph/update")
def graph_update(body: GraphUpdate):
    node = f"{body.tenant_id}:{body.user_id}:{body.device_id}:{body.epoch}"
    if body.context.get("cluster"):
        EDGES.append({"type":"cohab","src":node,"dst":f"cluster:{body.context['cluster']}","weight":0.6,"reason":"context_cluster"})
    if body.risk >= 80:
        EDGES.append({"type":"risk","src":node,"dst":"risk:high","weight":0.9,"reason":"high_risk"})
    return {"ok":True,"node":node,"edges":EDGES[-20:]}

@app.get("/graph/edges")
def graph_edges():
    return {"edges": EDGES[-200:]}
