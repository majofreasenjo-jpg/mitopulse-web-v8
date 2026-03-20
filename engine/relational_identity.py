import math

def relational_identity_score(G, node):
    if node not in G:
        return 0.0, {}
    degree = G.degree(node)
    customer_neighbors = device_neighbors = external_neighbors = suspicious_links = 0
    for nbr in G.neighbors(node):
        attrs = G.nodes[nbr]
        nt = attrs.get("node_type", "unknown")
        if nt == "customer": customer_neighbors += 1
        elif nt == "device": device_neighbors += 1
        else: external_neighbors += 1
        edge = G.get_edge_data(node, nbr, default={})
        if edge.get("label") in {"mule_pattern", "scam_ring", "social_chain"}:
            suspicious_links += 1
    stability = 1 / (1 + math.exp(-(customer_neighbors + device_neighbors - external_neighbors) / 3))
    contamination = min(1.0, suspicious_links * 0.18)
    score = max(0.0, min(1.0, 0.65 * stability + 0.20 * min(degree / 10, 1.0) - 0.35 * contamination))
    return round(score, 3), {
        "degree": degree,
        "customer_neighbors": customer_neighbors,
        "device_neighbors": device_neighbors,
        "external_neighbors": external_neighbors,
        "suspicious_links": suspicious_links,
        "stability_component": round(stability, 3),
        "contamination_component": round(contamination, 3),
    }
