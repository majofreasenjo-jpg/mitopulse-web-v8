from typing import Dict, List


def inject_shock(graph: Dict, source_symbol: str, initial_intensity: float = 1.0, decay: float = 0.72, max_hops: int = 3) -> Dict:
    adjacency: Dict[str, List[Dict]] = {}
    for edge in graph["edges"]:
        adjacency.setdefault(edge["source"], []).append(edge)

    frontier = [(source_symbol, initial_intensity, 0)]
    visited = []
    impacts = {source_symbol: initial_intensity}

    while frontier:
        symbol, intensity, hop = frontier.pop(0)
        visited.append({"symbol": symbol, "intensity": round(intensity, 4), "hop": hop})
        if hop >= max_hops:
            continue
        for edge in adjacency.get(symbol, []):
            weight = abs(float(edge["correlation"]))
            propagated = intensity * decay * weight
            if propagated < 0.05:
                continue
            tgt = edge["target"]
            impacts[tgt] = max(impacts.get(tgt, 0.0), propagated)
            frontier.append((tgt, propagated, hop + 1))

    return {
        "source": source_symbol,
        "visited": visited,
        "impact_map": {k: round(v, 4) for k, v in impacts.items()},
    }
