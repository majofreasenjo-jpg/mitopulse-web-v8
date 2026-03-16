import networkx as nx

def suspicious_clusters(G):
    clusters = []
    for comp in nx.connected_components(G):
        sub = G.subgraph(comp)
        suspicious_edges = 0
        suspicious_contexts = 0
        external = 0
        for _, attrs in sub.nodes(data=True):
            if attrs.get("node_type") == "external":
                external += 1
        for _, _, data in sub.edges(data=True):
            if data.get("label") in {"mule_pattern", "scam_ring", "social_chain"}:
                suspicious_edges += 1
            if data.get("context") in {"urgent_transfer", "social_engineering", "fake_receipt"}:
                suspicious_contexts += 1
        score = suspicious_edges * 0.08 + suspicious_contexts * 0.05 + max(0, external - 2) * 0.02
        if score >= 0.35:
            clusters.append({
                "cluster_size": len(comp),
                "external_nodes": external,
                "score": round(min(score, 0.99), 3),
                "sample_nodes": sorted(list(comp))[:12]
            })
    clusters.sort(key=lambda x: x["score"], reverse=True)
    return clusters
