from engine.relational_identity import relational_identity_score
from engine.relational_fingerprint import relational_fingerprint
from engine.trust_propagation import propagated_risk
from engine.relational_quorum import quorum_activation
from engine.stigmergic_trace import edge_trace_score
from engine.danger_signal import danger_signal_score
from engine.allostatic_reserve import reserve_components
from engine.reality_anchors import reality_anchor_score

def bioinspired_node_assessment(G, node):
    ri, ri_parts = relational_identity_score(G, node)
    fp = relational_fingerprint(G, node)
    pr, contributors = propagated_risk(G, node)
    st = edge_trace_score(G, node)
    dg = danger_signal_score(G, node)
    ra = reality_anchor_score(G, node)
    reserve = reserve_components(ri, dg["danger_score"], ra["reality_anchor_score"])
    q = quorum_activation([pr, st["stigmergic_trace"], dg["danger_score"]], [0.45, 0.25, 0.35], theta=0.80)
    trust_effective = max(0.0, min(1.0, 0.35 * ri + 0.20 * ra["reality_anchor_score"] + 0.25 * reserve["allostatic_reserve"] - 0.35 * dg["danger_score"]))
    risk = max(0.0, min(1.0, 0.40 * pr + 0.25 * st["stigmergic_trace"] + 0.35 * dg["danger_score"] + (0.10 if q["activated"] else 0.0) - 0.20 * ra["reality_anchor_score"]))
    risk = round(max(0.0, min(0.99, risk + (0.05 if fp["suspicious_edges"] >= 2 else 0.0))), 3)
    action = "BLOCK" if risk >= 0.80 else "REVIEW" if risk >= 0.45 else "ALLOW"
    return {"node": node, "recommended_action": action, "risk_score": risk, "trust_effective": round(trust_effective, 3), "relational_identity": ri, "relational_identity_parts": ri_parts, "relational_fingerprint": fp, "propagated_risk": pr, "propagation_contributors": contributors, "stigmergic_trace": st, "danger_signal": dg, "reality_anchor": ra, "allostatic": reserve, "quorum": q}

def portfolio_projection(G):
    allow = review = block = 0
    top = []
    for node, attrs in G.nodes(data=True):
        if attrs.get("node_type") != "customer":
            continue
        r = bioinspired_node_assessment(G, node)
        top.append(r)
        if r["recommended_action"] == "BLOCK": block += 1
        elif r["recommended_action"] == "REVIEW": review += 1
        else: allow += 1
    top.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"ALLOW": allow, "REVIEW": review, "BLOCK": block, "top": top[:20]}
