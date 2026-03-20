def reality_anchor_score(G, node):
    anchors = 0.0
    reasons = []
    attrs = G.nodes[node]
    if attrs.get("node_type") == "customer":
        anchors += 0.08
        reasons.append("customer_node")
    for nbr in G.neighbors(node):
        nattrs = G.nodes[nbr]
        if nattrs.get("node_type") == "device":
            anchors += 0.06
            reasons.append("trusted_device_link")
        edge = G.get_edge_data(node, nbr, default={})
        if edge.get("context") in {"salary", "family"}:
            anchors += 0.05
            reasons.append(edge.get("context"))
    return {"reality_anchor_score": round(min(anchors, 0.40), 3), "anchors": reasons[:10]}
