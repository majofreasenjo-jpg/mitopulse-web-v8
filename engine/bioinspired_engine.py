import math
import networkx as nx

def relational_identity_score(G, node):
    if node not in G:
        return 0.0
    degree = G.degree(node)
    customer_neighbors = device_neighbors = external_neighbors = suspicious_links = 0
    for nbr in G.neighbors(node):
        nt = G.nodes[nbr].get("node_type", "unknown")
        if nt == "customer":
            customer_neighbors += 1
        elif nt == "device":
            device_neighbors += 1
        else:
            external_neighbors += 1
        edge = G.get_edge_data(node, nbr, default={})
        if edge.get("label") in {"mule_pattern", "scam_ring", "social_chain"}:
            suspicious_links += 1
    stability = 1 / (1 + math.exp(-(customer_neighbors + device_neighbors - external_neighbors) / 3))
    contamination = min(1.0, suspicious_links * 0.18)
    return round(max(0.0, min(1.0, 0.65 * stability + 0.20 * min(degree / 10, 1.0) - 0.35 * contamination)), 3)

def propagated_risk(G, node, max_depth=2, beta=0.65):
    if node not in G:
        return 0.0
    risk = 0.0
    for other, attrs in G.nodes(data=True):
        sev = float(attrs.get("signal_severity", 0.0) or 0.0)
        if sev <= 0:
            continue
        try:
            depth = len(nx.shortest_path(G, node, other)) - 1
        except nx.NetworkXNoPath:
            continue
        if depth <= max_depth:
            risk += sev * (beta ** max(depth - 1, 0))
    return round(min(risk, 1.0), 3)

def stigmergic_trace(G, node):
    traces = []
    for nbr in G.neighbors(node):
        edge = G.get_edge_data(node, nbr, default={})
        base = 0.12 if edge.get("label") == "normal" else 0.55
        if edge.get("context") in {"urgent_transfer", "social_engineering", "fake_receipt", "sim_swap"}:
            base += 0.18
        traces.append(min(base, 1.0))
    if not traces:
        return 0.0
    trace = 0.0
    for t in traces:
        trace = 0.85 * trace + t
    return round(min(trace / max(len(traces), 1), 1.0), 3)

def danger_signal(G, node):
    danger = 0.0
    for nbr in G.neighbors(node):
        edge = G.get_edge_data(node, nbr, default={})
        if edge.get("label") in {"mule_pattern", "scam_ring", "social_chain"}:
            danger += 0.22
        if edge.get("context") in {"urgent_transfer", "social_engineering", "fake_receipt", "sim_swap", "identity_shift"}:
            danger += 0.18
    signal_type = G.nodes[node].get("signal_type")
    if signal_type in {"identity_shift", "sim_swap_hint", "shared_signal_detected", "device_reset"}:
        danger += 0.20
    return round(min(danger, 1.0), 3)

def reality_anchor(G, node):
    anchors = 0.0
    if G.nodes[node].get("node_type") == "customer":
        anchors += 0.08
    for nbr in G.neighbors(node):
        if G.nodes[nbr].get("node_type") == "device":
            anchors += 0.06
        edge = G.get_edge_data(node, nbr, default={})
        if edge.get("context") in {"salary", "family", "bill_payment", "payroll", "delivery_confirmed"}:
            anchors += 0.05
    return round(min(anchors, 0.40), 3)

def quorum_score(pr, st, dg, theta=0.80):
    total = 0.45 * pr + 0.25 * st + 0.35 * dg
    return round(total, 3), total >= theta

def calculate_pulse(ri, anchors, reserve, danger):
    """Layer 2: Pulse Engine"""
    health = (ri * 0.40) + (anchors * 0.30) + (reserve * 0.30)
    pulse = max(0.01, health - (danger * 0.50))
    return round(pulse, 3)

def cross_pulse(G, node, pulses):
    """Layer 3: Cross-Pulse Engine"""
    cp = 0.0
    for nbr in G.neighbors(node):
        edge = G.get_edge_data(node, nbr, default={})
        weight = 0.8 if edge.get("label") == "normal" else 1.5
        cp += pulses.get(node, 0.01) * pulses.get(nbr, 0.01) * weight
    return round(cp, 3)

def allostatic_reserve(ri, dg, ra):
    recovery = min(0.35, ri * 0.25 + ra)
    stress = min(0.60, dg * 0.55)
    return round(max(0.0, min(1.0, ri + recovery - stress)), 3)

def bioinspired_node_risk(G, node, pulses=None):
    if node not in G:
        return {"node": node, "immune_risk_score": 0.0, "recommended_action": "ALLOW"}
    ri = relational_identity_score(G, node)
    pr = propagated_risk(G, node)
    st = stigmergic_trace(G, node)
    dg = danger_signal(G, node)
    ra = reality_anchor(G, node)
    qscore, qactive = quorum_score(pr, st, dg)
    reserve = allostatic_reserve(ri, dg, ra)
    
    pulse = calculate_pulse(ri, ra, reserve, dg)
    if pulses is not None:
        pulses[node] = pulse
    cp = cross_pulse(G, node, pulses) if pulses else 0.0

    # Layer 8: Immune Risk Score
    irs_base = 0.40 * pr + 0.25 * st + 0.35 * dg + (0.10 if qactive else 0.0) - 0.20 * ra
    health_modifier = min(1.0, (1.0 - pulse) * 0.30 + (0.05 if cp > 0.8 else 0.0))
    
    irs = round(max(0.0, min(0.99, irs_base + health_modifier)), 3)
    action = "BLOCK" if irs >= 0.80 else "REVIEW" if irs >= 0.45 else "ALLOW"
    return {
        "node": node,
        "immune_risk_score": irs,
        "recommended_action": action,
        "relational_identity": ri,
        "propagated_risk": pr,
        "stigmergic_trace": st,
        "danger_signal": dg,
        "reality_anchor": ra,
        "allostatic_reserve": reserve,
        "quorum_score": qscore,
        "quorum_activated": qactive,
        "pulse_score": pulse,
        "cross_pulse_score": cp
    }

def bioinspired_projection(G):
    allow = review = block = 0
    top = []
    pulses = {}
    for node in G.nodes():
        pulses[node] = calculate_pulse(relational_identity_score(G, node), reality_anchor(G, node), allostatic_reserve(relational_identity_score(G, node), danger_signal(G, node), reality_anchor(G, node)), danger_signal(G, node))

    for node, attrs in G.nodes(data=True):
        if attrs.get("node_type") != "customer":
            continue
        r = bioinspired_node_risk(G, node, pulses)
        top.append(r)
        if r["recommended_action"] == "BLOCK":
            block += 1
        elif r["recommended_action"] == "REVIEW":
            review += 1
        else:
            allow += 1
    top.sort(key=lambda x: x["immune_risk_score"], reverse=True)
    return {"ALLOW": allow, "REVIEW": review, "BLOCK": block, "top": top[:20]}
