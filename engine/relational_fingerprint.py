import networkx as nx

def relational_fingerprint(G, node):
    if node not in G:
        return {"fingerprint": "unknown"}
    degree = G.degree(node)
    suspicious = 0
    contexts = set()
    for nbr in G.neighbors(node):
        edge = G.get_edge_data(node, nbr, default={})
        contexts.add(edge.get("context", "general"))
        if edge.get("label") in {"mule_pattern", "scam_ring", "social_chain"}:
            suspicious += 1
    try:
        clustering = nx.clustering(G, node)
    except Exception:
        clustering = 0.0
    motif = "star" if degree >= 6 and clustering < 0.10 else "clustered" if clustering >= 0.20 else "mixed"
    fp = f"d{degree}-c{round(clustering,2)}-s{suspicious}-m{motif}-ctx{len(contexts)}"
    return {"fingerprint": fp, "degree": degree, "clustering": round(clustering, 3), "suspicious_edges": suspicious, "motif": motif, "context_count": len(contexts)}
