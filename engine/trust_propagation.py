import networkx as nx

def propagated_risk(G, node, max_depth=2):
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
            risk += sev * (0.65 ** max(depth - 1, 0))
    return round(min(risk, 1.0), 3)
