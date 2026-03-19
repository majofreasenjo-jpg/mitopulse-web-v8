import json, math
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SEED = BASE / "data" / "graph_seed.json"

def load_seed():
    return json.loads(SEED.read_text(encoding="utf-8"))

def _kind_color(kind: str) -> str:
    return {
        "supply": "#4cc9f0",
        "storage": "#8ecae6",
        "process": "#ef476f",
        "logistics": "#ffd166",
        "commercial": "#7b61ff"
    }.get(kind, "#adb5bd")

def _pressure_score(node, ext_pressure: float, incoming_strength: float):
    raw = node["base_risk"] * 0.58 + ext_pressure * 0.22 + incoming_strength * 0.20
    return max(0.0, min(1.0, raw))

def build_live_graph():
    seed = load_seed()
    nodes = []
    links = []
    incoming = {n["id"]:0 for n in seed["nodes"]}
    for e in seed["edges"]:
        incoming[e["to"]] += e["weight"] * 0.45
    ext_pressure = sum(f["intensity"] for f in seed["external_fields"]) / max(1, len(seed["external_fields"]))

    for n in seed["nodes"]:
        score = _pressure_score(n, ext_pressure, incoming[n["id"]])
        role = "neutral"
        if score >= 0.82:
            role = "trigger"
        elif score >= 0.70:
            role = "hidden"
        elif score >= 0.58:
            role = "wave"
        nodes.append({
            "id": n["id"],
            "label": n["label"],
            "kind": n["kind"],
            "x": n["x_hint"],
            "y": n["y_hint"],
            "score": round(score, 3),
            "role": role,
            "color": _kind_color(n["kind"])
        })

    for e in seed["edges"]:
        links.append({
            "source": e["from"],
            "target": e["to"],
            "weight": e["weight"],
            "forecast_weight": round(min(1.0, e["weight"] * 1.06), 3)
        })

    risk_field = [{"x": n["x"], "y": n["y"], "intensity": n["score"]} for n in nodes]
    trigger_zones = [n["id"] for n in nodes if n["role"] == "trigger"]
    wave_fronts = [{"entity": n["id"], "x": n["x"], "y": n["y"], "intensity": n["score"], "speed": round(0.7 + n["score"], 2)} for n in nodes if n["role"] in ("wave","hidden","trigger")]

    return {
        "nodes": nodes,
        "links": links,
        "risk_field": risk_field,
        "trigger_zones": trigger_zones,
        "wave_fronts": wave_fronts,
        "external_pressure": round(ext_pressure, 3)
    }

def short_horizon_forecast(horizon: str = "short"):
    graph = build_live_graph()
    factor = {"short":1.08, "medium":1.18, "long":1.28}.get(horizon, 1.08)
    forecast_nodes = []
    max_score = 0
    for n in graph["nodes"]:
        propagated = min(0.99, n["score"] * factor)
        if n["role"] == "trigger":
            propagated = min(0.99, propagated + 0.05)
        max_score = max(max_score, propagated)
        forecast_nodes.append({
            "id": n["id"],
            "forecast_score": round(propagated, 3),
            "forecast_role": "critical" if propagated >= 0.84 else ("elevated" if propagated >= 0.68 else "stable")
        })

    forecasted_gsi = round(min(0.99, sum(n["forecast_score"] for n in forecast_nodes)/max(1, len(forecast_nodes)) * 1.05), 3)
    forecasted_scr = round(min(0.99, max_score * 0.92 + forecasted_gsi * 0.08), 3)
    propagation_path = [l["source"] + "->" + l["target"] for l in graph["links"] if l["forecast_weight"] >= 0.84]

    return {
        "horizon": horizon,
        "forecasted_GSI": forecasted_gsi,
        "forecasted_SCR": forecasted_scr,
        "node_forecasts": forecast_nodes,
        "propagation_path_forecast": propagation_path,
        "critical_window_probability": round(min(0.99, forecasted_scr * 0.9), 3)
    }

def invisible_storm_steps():
    graph = build_live_graph()
    steps = []
    stories = [
        "Weak anomalies emerge in supply and processing",
        "Pressure waves begin to cross the graph",
        "Propagation accelerates across the process chain",
        "A hidden storm starts forming around core units",
        "Critical window opens and action becomes urgent"
    ]
    for i in range(1, 21):
        p = i / 20.0
        gsi = min(0.99, 0.46 + p * 0.34)
        scr = min(0.99, 0.41 + p * 0.41)
        steps.append({
            "step": i,
            "phase": "emergence" if p < 0.34 else ("propagation" if p < 0.67 else "criticality"),
            "story": stories[min(4, int(p * 5))],
            "GSI": round(gsi, 3),
            "SCR": round(scr, 3),
            "forecasted_GSI": round(min(0.99, gsi * 1.08), 3),
            "forecasted_SCR": round(min(0.99, scr * 1.07), 3),
            "action_recommended": "enhanced_monitoring" if p < 0.55 else ("review_and_limit" if p < 0.8 else "continuity_protocol"),
            "graph": graph
        })
    return {"demo_name":"Invisible Storm Improved", "steps": steps}
