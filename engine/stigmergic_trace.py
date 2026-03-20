def update_trace(previous_trace, new_signal, rho=0.85):
    return round(rho * float(previous_trace) + float(new_signal), 3)

def edge_trace_score(G, node):
    traces = []
    for nbr in G.neighbors(node):
        edge = G.get_edge_data(node, nbr, default={})
        base = 0.15 if edge.get("label") == "normal" else 0.55
        if edge.get("context") in {"urgent_transfer", "social_engineering", "fake_receipt"}:
            base += 0.20
        traces.append(min(base, 1.0))
    if not traces:
        return {"stigmergic_trace": 0.0, "edge_count": 0}
    trace = 0.0
    for t in traces:
        trace = update_trace(trace, t)
    return {"stigmergic_trace": round(min(trace / max(len(traces), 1), 1.0), 3), "edge_count": len(traces)}
