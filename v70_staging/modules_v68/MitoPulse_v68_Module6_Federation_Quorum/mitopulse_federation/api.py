from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from mitopulse_federation.engine.quorum import weighted_quorum
from mitopulse_federation.engine.audit import build_federated_audit
from mitopulse_federation.network.registry import default_validators
from mitopulse_federation.network.broadcast import build_demo_votes

app = FastAPI(title="MitoPulse Federation API")

VALIDATORS = default_validators()


class VoteIn(BaseModel):
    entity_id: str
    node_id: str
    trust_weight: float
    decision: str
    confidence: float
    reason: Optional[str] = None


class BroadcastIn(BaseModel):
    entity_id: str
    signal: float


@app.get("/")
def root():
    return {"service": "mitopulse_federation", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok", "validators": len(VALIDATORS)}


@app.get("/validators")
def validators():
    return {"validators": VALIDATORS}


@app.post("/vote")
def vote(vote_in: VoteIn):
    quorum_result = weighted_quorum([vote_in.model_dump()])
    audit = build_federated_audit(vote_in.entity_id, vote_in.decision, [vote_in.model_dump()], quorum_result)
    return {"quorum": quorum_result, "audit": audit}


@app.post("/quorum/evaluate")
def quorum_evaluate(votes: List[VoteIn]):
    vote_dicts = [v.model_dump() for v in votes]
    quorum_result = weighted_quorum(vote_dicts)
    action = "approve"
    if quorum_result["approved"]:
        max_conf = max(v["confidence"] for v in vote_dicts)
        if max_conf >= 0.85:
            action = "block"
        elif max_conf >= 0.65:
            action = "restrict"
        else:
            action = "monitor"
    audit = build_federated_audit(vote_dicts[0]["entity_id"] if vote_dicts else "unknown", action, vote_dicts, quorum_result)
    return {"quorum": quorum_result, "action": action, "audit": audit}


@app.post("/federation/broadcast_demo")
def federation_broadcast_demo(req: BroadcastIn):
    votes = build_demo_votes(req.entity_id, req.signal, VALIDATORS)
    quorum_result = weighted_quorum(votes)
    action = "approve"
    if quorum_result["approved"]:
        if req.signal >= 0.85:
            action = "block"
        elif req.signal >= 0.65:
            action = "restrict"
        elif req.signal >= 0.45:
            action = "monitor"
        else:
            action = "approve"
    audit = build_federated_audit(req.entity_id, action, votes, quorum_result)
    return {"votes": votes, "quorum": quorum_result, "action": action, "audit": audit}
