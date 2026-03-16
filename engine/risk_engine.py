from collections import Counter
from engine.trust_propagation import propagated_risk

def node_risk(G, node):
    if node not in G:
        return {"node": node, "risk_score": 0.0, "recommended_action": "ALLOW", "reason": "unknown"}
    attrs = G.nodes[node]
    degree = G.degree(node)
    direct = float(attrs.get("signal_severity", 0.0) or 0.0)
    prop = propagated_risk(G, node)
    suspicious = 0
    contexts = Counter()
    for nbr in G.neighbors(node):
        edge = G.get_edge_data(node, nbr, default={})
        contexts[edge.get("context", "general")] += 1
        if edge.get("label") in {"mule_pattern", "scam_ring", "social_chain"}:
            suspicious += 1
    risk = 0.07 + min(0.20, degree * 0.015) + direct * 0.33 + prop * 0.30 + min(0.28, suspicious * 0.07)
    if contexts["social_engineering"] > 0: risk += 0.12
    if contexts["fake_receipt"] > 0: risk += 0.10
    if contexts["urgent_transfer"] > 1: risk += 0.08
    risk = round(min(risk, 0.99), 3)
    action = "BLOCK" if risk >= 0.80 else "REVIEW" if risk >= 0.45 else "ALLOW"
    return {
        "node": node,
        "risk_score": risk,
        "recommended_action": action,
        "reason": "high_relational_risk" if action == "BLOCK" else "elevated_relational_risk" if action == "REVIEW" else "normal_profile",
        "direct_signal": direct,
        "propagated_risk": prop,
        "degree": degree
    }

def decision_projection(G):
    allow = review = block = 0
    top = []
    for n, attrs in G.nodes(data=True):
        if attrs.get("node_type") != "customer":
            continue
        r = node_risk(G, n)
        top.append(r)
        if r["recommended_action"] == "BLOCK": block += 1
        elif r["recommended_action"] == "REVIEW": review += 1
        else: allow += 1
    top.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"ALLOW": allow, "REVIEW": review, "BLOCK": block, "top_risky_customers": top[:15]}
