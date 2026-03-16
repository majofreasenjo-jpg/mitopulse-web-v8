from collections import Counter

def baseline_node_risk(G, node):
    if node not in G:
        return {"node": node, "risk_score": 0.0, "recommended_action": "ALLOW"}
    degree = G.degree(node)
    suspicious = 0
    contexts = Counter()
    direct_signal = float(G.nodes[node].get("signal_severity", 0.0) or 0.0)
    for nbr in G.neighbors(node):
        edge = G.get_edge_data(node, nbr, default={})
        contexts[edge.get("context", "general")] += 1
        if edge.get("label") in {"mule_pattern", "scam_ring", "social_chain"}:
            suspicious += 1
    risk = 0.05 + min(0.15, degree * 0.01) + direct_signal * 0.25 + min(0.22, suspicious * 0.06)
    if contexts["urgent_transfer"] > 1:
        risk += 0.06
    if contexts["fake_receipt"] > 0:
        risk += 0.08
    risk = round(min(risk, 0.99), 3)
    action = "BLOCK" if risk >= 0.82 else "REVIEW" if risk >= 0.50 else "ALLOW"
    return {"node": node, "risk_score": risk, "recommended_action": action}

def baseline_projection(G):
    allow = review = block = 0
    top = []
    for node, attrs in G.nodes(data=True):
        if attrs.get("node_type") != "customer":
            continue
        r = baseline_node_risk(G, node)
        top.append(r)
        if r["recommended_action"] == "BLOCK":
            block += 1
        elif r["recommended_action"] == "REVIEW":
            review += 1
        else:
            allow += 1
    top.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"ALLOW": allow, "REVIEW": review, "BLOCK": block, "top": top[:20]}
