
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
import hashlib
import math
import random

app = FastAPI(title="MitoPulse v11")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")

# -------------------------
# In-memory demo stores
# -------------------------
nodes = {}
relationships = {}
evaluations = []
cross_pulses = []
guardian_log = []
fraud_flags = set()

def now():
    return datetime.utcnow().isoformat()

def rel_key(a, b):
    return "::".join(sorted([a, b]))

def ensure_node(node_id: str, user_id: str | None = None):
    if node_id not in nodes:
        nodes[node_id] = {
            "node_id": node_id,
            "user_id": user_id or node_id.replace("node_", "usr_"),
            "pulse_count": 0,
            "cross_pulse_count": 0,
            "last_seen_at": None,
            "nodal_mass": 10.0,
            "trust_rank": 50.0,
            "status": "healthy",
            "guardian_score": 0.0,
            "is_guardian": False,
            "fraud_exposure": 0.0,
            "created_at": now(),
        }
    return nodes[node_id]

def ensure_relationship(a: str, b: str):
    key = rel_key(a, b)
    if key not in relationships:
        relationships[key] = {
            "a": a,
            "b": b,
            "weight": 20.0,
            "interactions": 0,
            "shared_reality_avg": 0.0,
            "last_interaction_at": None,
        }
    return relationships[key]

def calculate_guardian_score(node_id: str):
    node = nodes[node_id]
    degree = sum(1 for r in relationships.values() if node_id in (r["a"], r["b"]))
    rels = [r for r in relationships.values() if node_id in (r["a"], r["b"])]
    avg_weight = sum(r["weight"] for r in rels) / len(rels) if rels else 0
    exposure_penalty = node["fraud_exposure"]
    pulse_factor = min(100, node["pulse_count"] * 2)
    cross_factor = min(100, node["cross_pulse_count"] * 4)
    mass_factor = min(100, node["nodal_mass"])
    trust_factor = max(0, min(100, node["trust_rank"]))
    stability = min(100, degree * 8 + avg_weight * 0.4)

    score = (
        0.18 * stability
        + 0.18 * trust_factor
        + 0.15 * mass_factor
        + 0.12 * pulse_factor
        + 0.17 * cross_factor
        + 0.20 * (100 - exposure_penalty)
    )
    node["guardian_score"] = round(score, 2)
    node["is_guardian"] = score >= 72 and exposure_penalty < 25 and degree >= 2
    return node["guardian_score"]

def update_all_guardians():
    changed = []
    for node_id in list(nodes.keys()):
        before = nodes[node_id]["is_guardian"]
        score = calculate_guardian_score(node_id)
        after = nodes[node_id]["is_guardian"]
        if before != after:
            changed.append({"node_id": node_id, "guardian": after, "score": score, "time": now()})
    if changed:
        guardian_log.extend(changed)
    return changed

def calculate_fraud_exposure(node_id: str):
    base = 0.0
    for r in relationships.values():
        if node_id in (r["a"], r["b"]):
            other = r["b"] if r["a"] == node_id else r["a"]
            if other in fraud_flags:
                base += min(25, r["weight"] * 0.4)
            base += nodes.get(other, {}).get("fraud_exposure", 0) * 0.05
    nodes[node_id]["fraud_exposure"] = round(min(100, base), 2)
    return nodes[node_id]["fraud_exposure"]

def update_status(node_id: str):
    exposure = nodes[node_id]["fraud_exposure"]
    if exposure >= 70:
        status = "quarantined"
    elif exposure >= 45:
        status = "high_risk"
    elif exposure >= 20:
        status = "monitored"
    else:
        status = "healthy"
    nodes[node_id]["status"] = status
    return status

def compute_trust_breakdown(source_node_id: str, target_node_id: str, amount_anomaly: float, routine_break: float, industry: str):
    rel = relationships.get(rel_key(source_node_id, target_node_id))
    rds = min(100, rel["weight"]) if rel else 0
    target = ensure_node(target_node_id)
    ass = round((target["guardian_score"] * 0.5) + (min(100, target["nodal_mass"]) * 0.25) + (min(100, target["trust_rank"]) * 0.25), 2)
    srs = round(min(100, 30 + target["cross_pulse_count"] * 5 + (15 if rel else 0)), 2)
    novelty = 100 if not rel else max(0, 100 - rel["weight"])
    sc = round(max(0, 100 - ((amount_anomaly * 100 + routine_break * 100 + novelty) / 3)), 2)
    fe = round(target["fraud_exposure"], 2)
    trust = round(0.25*rds + 0.25*ass + 0.25*srs + 0.25*sc - fe, 2)
    if trust >= 80:
        decision = "VERIFY"
        action = "allow"
    elif trust >= 60:
        decision = "REVIEW"
        action = "step_up_authentication"
    else:
        decision = "BLOCK"
        action = "step_up_authentication"
    return {
        "rds": round(rds, 2),
        "ass": round(ass, 2),
        "srs": round(srs, 2),
        "sc": round(sc, 2),
        "fe": fe,
        "trust_score": trust,
        "decision": decision,
        "recommended_action": action,
        "industry": industry,
    }

def audit_receipt(source: str, target: str, bd: dict):
    raw = json_dumps({"source": source, "target": target, "breakdown": bd, "ts": now()})
    return hashlib.sha256(raw.encode()).hexdigest()[:24]

def json_dumps(x):
    import json
    return json.dumps(x, sort_keys=True)

# -------------------------
# Seed demo network
# -------------------------
def seed_demo_network():
    if nodes:
        return
    names = ["manuel","sofia","carlos","elena","marco","valen","lucas","amy","diego","sara","tom","mia"]
    for i, n in enumerate(names, start=1):
        ensure_node(f"node_{i}", f"usr_{n}")
        nodes[f"node_{i}"]["pulse_count"] = random.randint(3, 15)
        nodes[f"node_{i}"]["cross_pulse_count"] = random.randint(1, 12)
        nodes[f"node_{i}"]["nodal_mass"] = random.randint(20, 95)
        nodes[f"node_{i}"]["trust_rank"] = random.randint(35, 92)
    pairs = [
        ("node_1","node_2"),("node_1","node_3"),("node_2","node_4"),("node_3","node_5"),
        ("node_4","node_6"),("node_5","node_6"),("node_6","node_7"),("node_7","node_8"),
        ("node_8","node_9"),("node_9","node_10"),("node_1","node_10"),("node_2","node_9")
    ]
    for a, b in pairs:
        rel = ensure_relationship(a, b)
        rel["weight"] = random.randint(28, 88)
        rel["interactions"] = random.randint(2, 30)
        rel["shared_reality_avg"] = random.randint(35, 90)
        rel["last_interaction_at"] = now()
    fraud_flags.add("node_10")
    fraud_flags.add("node_9")
    for nid in list(nodes.keys()):
        calculate_fraud_exposure(nid)
        update_status(nid)
    update_all_guardians()

seed_demo_network()

# -------------------------
# Schemas
# -------------------------
class RegisterNode(BaseModel):
    node_id: str
    user_id: str | None = None

class PulseIn(BaseModel):
    node_id: str

class CrossPulseIn(BaseModel):
    node_a: str
    node_b: str
    shared_context_score: float = 82
    temporal_delta_ms: int = 35
    source: str = "manual"

class EvalIn(BaseModel):
    source_node_id: str
    target_node_id: str
    industry: str = "banking"
    amount_anomaly: float = 0.0
    routine_break: float = 0.0

# -------------------------
# Routes: pages
# -------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/network", response_class=HTMLResponse)
def network_page(request: Request):
    return templates.TemplateResponse("network.html", {"request": request})

@app.get("/node", response_class=HTMLResponse)
def node_page(request: Request):
    return templates.TemplateResponse("node.html", {"request": request})

@app.get("/simulator", response_class=HTMLResponse)
def simulator_page(request: Request):
    return templates.TemplateResponse("simulator.html", {"request": request})

# -------------------------
# Routes: API
# -------------------------
@app.post("/api/register_node")
def api_register_node(payload: RegisterNode):
    node = ensure_node(payload.node_id, payload.user_id)
    update_all_guardians()
    return node

@app.post("/api/pulse")
def api_pulse(payload: PulseIn):
    node = ensure_node(payload.node_id)
    node["pulse_count"] += 1
    node["last_seen_at"] = now()
    node["nodal_mass"] = round(min(100, node["nodal_mass"] + 1.0), 2)
    calculate_guardian_score(payload.node_id)
    return {
        "node_id": payload.node_id,
        "pulse_count": node["pulse_count"],
        "last_seen_at": node["last_seen_at"],
        "guardian_score": node["guardian_score"],
        "is_guardian": node["is_guardian"],
    }

@app.get("/api/nodes")
def api_nodes():
    out = []
    for nid, node in nodes.items():
        out.append(node)
    return out

@app.post("/api/crosspulse")
def api_crosspulse(payload: CrossPulseIn):
    ensure_node(payload.node_a)
    ensure_node(payload.node_b)
    before = ensure_relationship(payload.node_a, payload.node_b)["weight"]
    rel = ensure_relationship(payload.node_a, payload.node_b)
    rel["interactions"] += 1
    rel["weight"] = round(min(100, rel["weight"] + max(1.0, payload.shared_context_score / 25)), 2)
    rel["shared_reality_avg"] = round((rel["shared_reality_avg"] + payload.shared_context_score) / 2, 2)
    rel["last_interaction_at"] = now()
    nodes[payload.node_a]["cross_pulse_count"] += 1
    nodes[payload.node_b]["cross_pulse_count"] += 1
    nodes[payload.node_a]["nodal_mass"] = round(min(100, nodes[payload.node_a]["nodal_mass"] + 0.6), 2)
    nodes[payload.node_b]["nodal_mass"] = round(min(100, nodes[payload.node_b]["nodal_mass"] + 0.6), 2)
    event = {
        "crosspulse_id": f"cp_{len(cross_pulses)+1}",
        "node_a": payload.node_a,
        "node_b": payload.node_b,
        "shared_context_score": payload.shared_context_score,
        "temporal_delta_ms": payload.temporal_delta_ms,
        "relationship_weight_before": before,
        "relationship_weight_after": rel["weight"],
        "source": payload.source,
        "time": now()
    }
    cross_pulses.append(event)
    for nid in [payload.node_a, payload.node_b]:
        calculate_fraud_exposure(nid)
        update_status(nid)
        calculate_guardian_score(nid)
    return event

@app.post("/api/evaluate")
def api_evaluate(payload: EvalIn):
    ensure_node(payload.source_node_id)
    ensure_node(payload.target_node_id)
    breakdown = compute_trust_breakdown(
        payload.source_node_id,
        payload.target_node_id,
        payload.amount_anomaly,
        payload.routine_break,
        payload.industry,
    )
    if breakdown["decision"] == "BLOCK":
        fraud_flags.add(payload.target_node_id)
    calculate_fraud_exposure(payload.target_node_id)
    update_status(payload.target_node_id)
    update_all_guardians()
    evaluation_id = f"ev_{len(evaluations)+1}"
    audit = {
        "evaluation_id": evaluation_id,
        "timestamp": now(),
        "source_node_id": payload.source_node_id,
        "target_node_id": payload.target_node_id,
        "decision": breakdown["decision"],
        "trust_score": breakdown["trust_score"],
        "breakdown": {
            "RDS": breakdown["rds"],
            "ASS": breakdown["ass"],
            "SRS": breakdown["srs"],
            "SC": breakdown["sc"],
            "FE": breakdown["fe"],
        },
        "human_explanation": {
            "RDS": "Relación previa y cercanía en el grafo.",
            "ASS": "Soporte del destino por guardianes, masa nodal y confianza.",
            "SRS": "Señales de realidad compartida y evidencia relacional.",
            "SC": "Coherencia del contexto, monto y rutina.",
            "FE": "Exposición del nodo destino a fraude propagado.",
        },
        "recommended_action": breakdown["recommended_action"],
    }
    audit["audit_receipt"] = audit_receipt(payload.source_node_id, payload.target_node_id, breakdown)
    evaluations.append(audit)
    return audit

@app.get("/api/evaluation/{evaluation_id}/audit")
def api_audit(evaluation_id: str):
    for e in evaluations:
        if e["evaluation_id"] == evaluation_id:
            return e
    return JSONResponse({"error": "not_found"}, status_code=404)

@app.get("/api/fraud_clusters")
def api_fraud_clusters():
    clusters = []
    seen = set()
    for flagged in list(fraud_flags):
        if flagged in seen:
            continue
        infected = []
        for r in relationships.values():
            if flagged in (r["a"], r["b"]):
                infected.append(r["b"] if r["a"] == flagged else r["a"])
        seen.add(flagged)
        spread_level = "high" if len(infected) >= 3 else "medium" if infected else "low"
        clusters.append({
            "root_node": flagged,
            "infected_nodes": len(infected),
            "spread_level": spread_level,
            "neighbors": infected
        })
    return {"clusters": clusters}

@app.get("/api/spread_map")
def api_spread_map():
    paths = []
    for flagged in fraud_flags:
        for r in relationships.values():
            if flagged in (r["a"], r["b"]):
                other = r["b"] if r["a"] == flagged else r["a"]
                paths.append({
                    "from": flagged,
                    "to": other,
                    "weight": r["weight"],
                    "risk_to": nodes.get(other, {}).get("fraud_exposure", 0),
                })
    return {"paths": paths}

@app.get("/api/guardian_algorithm")
def api_guardian_algorithm():
    return {
        "formula": "guardian_score = 0.18*stability + 0.18*trust_rank + 0.15*nodal_mass + 0.12*pulse_factor + 0.17*cross_factor + 0.20*(100-fraud_exposure)",
        "threshold": "guardian if score >= 72, fraud_exposure < 25, degree >= 2",
        "variables": {
            "stability": "degree and average relationship weight",
            "trust_rank": "local trust estimate of node",
            "nodal_mass": "accumulated mass by events",
            "pulse_factor": "heartbeat activity",
            "cross_factor": "cross-pulse activity",
            "fraud_exposure": "risk propagated from neighboring nodes"
        }
    }

@app.get("/api/ecosystem_map")
def api_ecosystem_map():
    return {
        "layers": [
            "Users / Devices",
            "Client Apps / Wallets / Marketplaces / Banks",
            "MitoPulse SDK",
            "MitoPulse API",
            "Trust Graph + Fraud Hunter + Relay",
            "Decision Engine",
            "Global Fraud Memory"
        ],
        "modules": [
            "Trust Graph Engine",
            "Shared Reality / MitoRelay",
            "Fraud Hunter Engine",
            "Guardian Nodes",
            "Fraud Spread Engine",
            "Audit Layer",
            "Industry Modules"
        ]
    }
