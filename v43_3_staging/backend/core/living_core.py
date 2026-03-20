import math

def compute_kpis(entities):
    vals = [e.get("value",0) for e in entities]
    avg = sum(vals)/max(1,len(vals))
    nhi = round(max(0, 100 - avg * 0.42), 2)
    tpi = round(min(100, avg * 0.61), 2)
    scr = round(min(100, (100 - nhi) * 0.44 + tpi * 0.56), 2)
    mdi = round(min(100, max(vals) * 0.72), 2)
    metabolic_load = round(avg * 0.88, 2)
    homeostasis = round(max(0, 100 - abs(50 - nhi) * 0.8 - tpi * 0.22), 2)
    reflex_count = 1 if scr >= 70 else 0
    pai = round(min(100, tpi * 0.7 + mdi * 0.2), 2)
    return {
        "NHI": nhi, "TPI": tpi, "SCR": scr, "MDI": mdi,
        "Metabolic Load": metabolic_load,
        "Homeostasis Stability Score": homeostasis,
        "Reflex Activation Count": reflex_count,
        "Pressure Accumulation Index": pai
    }

def build_graph(entities):
    nodes = []
    links = []
    cx, cy = 520, 260
    n = max(1, len(entities))
    for i, e in enumerate(entities):
        angle = 2 * math.pi * i / n
        radius = 150 + e["value"] * 1.3
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        role = "neutral"
        if e["value"] >= 90: role = "trigger"
        elif e["value"] >= 75: role = "hidden"
        elif e["value"] >= 60: role = "wave"
        nodes.append({
            "id": e["id"], "label": e["id"], "kind": e["kind"],
            "x": round(x,2), "y": round(y,2), "score": e["value"], "role": role
        })
    for i in range(len(nodes)-1):
        links.append({"source": nodes[i]["id"], "target": nodes[i+1]["id"], "weight": 50 + i*7})
    waves = [{"entity": n["id"], "x": n["x"], "y": n["y"], "intensity": round(n["score"]/100,2)} for n in nodes if n["score"] >= 60]
    return {
        "nodes": nodes,
        "links": links,
        "dynamic_waves": waves,
        "risk_field": [{"x": n["x"], "y": n["y"], "intensity": round(n["score"]/100,2)} for n in nodes],
        "trigger_zones": [n["id"] for n in nodes if n["role"]=="trigger"]
    }

def system_brain(entities):
    critical_nodes = [e["id"] for e in entities if e["value"] >= 80]
    return {
        "pulse_inputs": len(entities),
        "critical_nodes": critical_nodes,
        "decision_trace": [
            "signals ingested",
            "metabolic load updated",
            "behavioral profile enriched",
            "RFDC pressure computed",
            "action threshold evaluated"
        ]
    }

def alerts_and_action(kpis, client_mode="full"):
    scr = kpis["SCR"]
    if client_mode == "marketplace":
        action = "freeze payouts" if scr >= 70 else "manual review"
        recipient = "Trust & Safety"
        top_risk = "coordinated seller risk"
    elif client_mode == "energy":
        action = "continuity protocol" if scr >= 70 else "dispatch prioritization"
        recipient = "COO / Operations Risk"
        top_risk = "refinery instability cascade"
    elif client_mode == "bank":
        action = "freeze account" if scr >= 70 else "fraud review"
        recipient = "Fraud / AML"
        top_risk = "money mule coordination"
    else:
        action = "review_and_limit" if scr >= 60 else "enhanced_monitoring"
        recipient = "Risk Ops"
        top_risk = "systemic coordination risk"
    return {
        "top_risk": top_risk,
        "recommended_action": action,
        "recipient": recipient,
        "severity": "critical" if scr >= 70 else ("high" if scr >= 45 else "medium")
    }
