def danger_signal_score(G, node):
    danger = 0.0
    events = []
    for nbr in G.neighbors(node):
        edge = G.get_edge_data(node, nbr, default={})
        label = edge.get("label", "normal")
        context = edge.get("context", "general")
        if label in {"mule_pattern", "scam_ring", "social_chain"}:
            danger += 0.22
            events.append(label)
        if context in {"urgent_transfer", "social_engineering", "fake_receipt"}:
            danger += 0.18
            events.append(context)
    attrs = G.nodes[node]
    signal_type = attrs.get("signal_type")
    if signal_type in {"identity_shift", "sim_swap_hint", "shared_signal_detected", "device_reset"}:
        danger += 0.20
        events.append(signal_type)
    return {"danger_score": round(min(danger, 1.0), 3), "danger_events": events[:12]}
