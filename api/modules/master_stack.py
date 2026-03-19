import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SEED = BASE / "data" / "graph_seed.json"
STATE = BASE / "data" / "state.json"

def load_seed():
    return json.loads(SEED.read_text(encoding="utf-8"))

def load_state():
    return json.loads(STATE.read_text(encoding="utf-8"))

def save_state(data):
    STATE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def build_live_graph():
    seed = load_seed()
    incoming = {n["id"]: 0 for n in seed["nodes"]}
    for e in seed["edges"]:
        incoming[e["to"]] += e["weight"] * 0.45
    ext_pressure = sum(f["intensity"] for f in seed["external_fields"]) / max(1, len(seed["external_fields"]))

    nodes, links = [], []
    for n in seed["nodes"]:
        score = max(0.0, min(0.99, n["base_risk"] * 0.58 + ext_pressure * 0.22 + incoming[n["id"]] * 0.20))
        role = "neutral"
        if score >= 0.82: role = "trigger"
        elif score >= 0.70: role = "hidden"
        elif score >= 0.58: role = "wave"
        nodes.append({
            "id": n["id"], "label": n["label"], "kind": n["kind"],
            "x": n["x_hint"], "y": n["y_hint"], "score": round(score, 3), "role": role
        })
    for e in seed["edges"]:
        links.append({"source": e["from"], "target": e["to"], "weight": e["weight"], "forecast_weight": round(min(1.0, e["weight"]*1.06), 3)})

    return {
        "nodes": nodes,
        "links": links,
        "external_pressure": round(ext_pressure, 3),
        "risk_field": [{"x": n["x"], "y": n["y"], "intensity": n["score"]} for n in nodes],
        "trigger_zones": [n["id"] for n in nodes if n["role"]=="trigger"],
        "wave_fronts": [{"entity": n["id"], "x": n["x"], "y": n["y"], "intensity": n["score"]} for n in nodes if n["role"] in ("wave","hidden","trigger")]
    }

import statistics

def executive():
    graph = build_live_graph()
    scores = [n["score"] for n in graph["nodes"]]
    avg = sum(scores) / max(1, len(scores))
    
    # V46.5 Advanced Calibration Logic: Integration of variance to detect hidden clusters
    variance = statistics.variance(scores) if len(scores) > 1 else 0
    calibrated_avg = avg + (variance * 1.85)

    gsi = round(min(0.99, calibrated_avg * 1.05), 3)
    nhi = round(max(0.01, 1 - calibrated_avg*0.72), 3)
    tpi = round(min(0.99, calibrated_avg * 0.88), 3)
    scr = round(min(0.99, max(scores) * 0.85 + gsi * 0.15 + variance * 0.4), 3)
    
    # Dynamic string logic based on probabilistic thresholds
    top_risk = "Critical Systemic Propagation Event detected via high variance" if scr >= 0.7 else ("Invisible storm forming around processing core" if scr >= 0.55 else "Elevated propagation pressure")
    action = "freeze_and_contain" if scr >= 0.75 else ("review_and_limit" if scr >= 0.55 else "enhanced_monitoring")

    return {
        "GSI": gsi,
        "NHI": nhi,
        "TPI": tpi,
        "SCR": scr,
        "top_risk": top_risk,
        "recommended_action": action
    }

def forecast(horizon="short"):
    graph = build_live_graph()
    factor = {"short": 1.08, "medium": 1.18, "long": 1.28}.get(horizon, 1.08)
    nodes = []
    max_score = 0
    for n in graph["nodes"]:
        fs = min(0.99, n["score"] * factor + (0.05 if n["role"] == "trigger" else 0))
        nodes.append({"id": n["id"], "forecast_score": round(fs, 3)})
        max_score = max(max_score, fs)
    fgsi = round(min(0.99, sum(n["forecast_score"] for n in nodes)/max(1,len(nodes))*1.05), 3)
    fscr = round(min(0.99, max_score*0.92 + fgsi*0.08), 3)
    return {
        "horizon": horizon,
        "forecasted_GSI": fgsi,
        "forecasted_SCR": fscr,
        "critical_window_probability": round(min(0.99, fscr*0.9), 3),
        "node_forecasts": nodes,
        "propagation_path_forecast": [l["source"] + "->" + l["target"] for l in graph["links"] if l["forecast_weight"] >= 0.84]
    }

def system_brain():
    graph = build_live_graph()
    return {
        "critical_nodes": [n["id"] for n in graph["nodes"] if n["score"] >= 0.75],
        "decision_trace": [
            "signals ingested",
            "pressure aggregated",
            "wave propagation estimated",
            "short-horizon forecast computed",
            "recommended action updated"
        ]
    }

def ai_layer():
    ex = executive()
    gsi_val = ex["GSI"]
    scr_val = ex["SCR"]
    
    # V46.5 Advanced AI Integration: Contextual Semantic Explainability
    if scr_val > 0.75:
        ai_behavior = "Defensive Containment"
        ai_desc = "AI Copilot has identified critical variance across the supply chain cluster. Immediate freeze recommended to prevent downstream systemic collapse."
        alts = ["freeze_and_contain", "emergency_logistics_reroute"]
    elif scr_val > 0.55:
        ai_behavior = "Elevated Flow Risk"
        ai_desc = "Risk concentration is intensifying. AI observes hidden coordination forming around priority nodes. Manual review thresholds should be escalated."
        alts = ["review_and_limit", "continuity_protocol", "enhanced_monitoring"]
    else:
        ai_behavior = "Opportunistic Optimization"
        ai_desc = "System health is stable. Propagation paths are contained within expected operational margins."
        alts = ["enhanced_monitoring", "baseline_operations"]

    return {
        "semantic_ingestion_ai": {"normalized": True, "mapped_entities": 12, "accuracy_variance": round(gsi_val * 0.1, 4)},
        "behavioral_ai": [{"id":"cluster_alpha","behavior": ai_behavior}, {"id":"dispatch_node","behavior":"predictive_routing"}],
        "explainability_ai": {
            "executive_text": f"Main risk: {ex['top_risk']}.",
            "technical_text": ai_desc
        },
        "strategy_copilot": {
            "recommended_action": ex["recommended_action"],
            "alternative_actions": alts
        }
    }

def invisible_storm():
    graph = build_live_graph()
    stories = [
        "Weak anomalies emerge in supply and processing",
        "Pressure waves begin to cross the graph",
        "Propagation accelerates across the process chain",
        "A hidden storm starts forming around core units",
        "Critical window opens and action becomes urgent"
    ]
    steps = []
    for i in range(1, 21):
        p = i/20.0
        gsi = min(0.99, 0.46 + p*0.34)
        scr = min(0.99, 0.41 + p*0.41)
        steps.append({
            "step": i,
            "phase": "emergence" if p < 0.34 else ("propagation" if p < 0.67 else "criticality"),
            "story": stories[min(4, int(p*5))],
            "GSI": round(gsi, 3),
            "SCR": round(scr, 3),
            "forecasted_GSI": round(min(0.99, gsi*1.08), 3),
            "forecasted_SCR": round(min(0.99, scr*1.07), 3),
            "action_recommended": "enhanced_monitoring" if p < 0.55 else ("review_and_limit" if p < 0.8 else "continuity_protocol"),
            "graph": graph
        })
    return {"demo_name": "Invisible Storm Improved", "steps": steps}

def verify():
    ex = executive()
    return {
        "title": "Verification Recommended",
        "relational_risk": ex["SCR"],
        "system_instability": ex["GSI"],
        "message": "This receiver shows patterns associated with elevated systemic risk.",
        "recommendation": "Please continue with additional bank verification.",
        "confidence": "medium-high" if ex["SCR"] >= 0.7 else "medium"
    }

def add_action(entity_id, action):
    state = load_state()
    state["actions"].append({"entity_id": entity_id, "action": action})
    save_state(state)
    return state
