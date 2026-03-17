from __future__ import annotations
from collections import Counter
import math
import networkx as nx
import pandas as pd


def relational_identity_score(G: nx.Graph, node: str) -> float:
    if node not in G:
        return 0.0
    degree = G.degree(node)
    cust = dev = ext = suspicious = 0
    for nbr in G.neighbors(node):
        ntype = G.nodes[nbr].get("node_type", "unknown")
        cust += ntype == "customer"
        dev += ntype == "device"
        ext += ntype == "external"
        edge = G.get_edge_data(node, nbr, default={})
        suspicious += edge.get("label") in {"mule_pattern", "scam_ring", "social_chain", "historical_stress"}
    stability = 1 / (1 + math.exp(-(cust + dev - ext) / 3))
    contamination = min(1.0, suspicious * 0.18)
    return round(max(0.0, min(1.0, 0.65 * stability + 0.20 * min(degree / 10, 1.0) - 0.35 * contamination)), 3)


def pulse_series(events_df: pd.DataFrame, windows: int = 8) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}
    if "source_id" not in events_df:
        return out
    if "timestamp" not in events_df:
        grouped = events_df.groupby("source_id").size().to_dict()
        return {k: [float(v)] for k, v in grouped.items()}
    temp = events_df.copy()
    temp["timestamp"] = pd.to_datetime(temp["timestamp"], errors="coerce")
    temp = temp.dropna(subset=["timestamp"])
    if temp.empty:
        grouped = events_df.groupby("source_id").size().to_dict()
        return {k: [float(v)] for k, v in grouped.items()}
    temp["bucket"] = pd.qcut(temp["timestamp"].rank(method="first"), q=min(windows, len(temp)), labels=False, duplicates="drop")
    for node, grp in temp.groupby("source_id"):
        counts = grp.groupby("bucket").size()
        out[str(node)] = [float(counts.get(i, 0.0)) for i in range(int(temp["bucket"].max()) + 1)]
    return out


def safe_corr(a: list[float], b: list[float]) -> float:
    m = max(len(a), len(b))
    if m == 0:
        return 0.0
    a = a + [0.0] * (m - len(a))
    b = b + [0.0] * (m - len(b))
    if len(set(a)) == 1 and len(set(b)) == 1:
        return 1.0 if a == b else 0.0
    sa = pd.Series(a)
    sb = pd.Series(b)
    c = sa.corr(sb)
    return round(float(0.0 if pd.isna(c) else c), 3)


def cross_pulse_pairs(events_df: pd.DataFrame, top_n: int = 12) -> list[dict]:
    series = pulse_series(events_df)
    nodes = list(series.keys())[:60]
    pairs = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            corr = safe_corr(series[nodes[i]], series[nodes[j]])
            if corr > 0.55:
                pairs.append({"a": nodes[i], "b": nodes[j], "sync": corr})
    pairs.sort(key=lambda x: x["sync"], reverse=True)
    return pairs[:top_n]


def danger_signal_score(G: nx.Graph, node: str) -> float:
    danger = 0.0
    if node not in G:
        return 0.0
    for nbr in G.neighbors(node):
        edge = G.get_edge_data(node, nbr, default={})
        if edge.get("label") in {"mule_pattern", "scam_ring", "social_chain", "historical_stress"}:
            danger += 0.22
        if edge.get("context") in {"urgent_transfer", "social_engineering", "fake_receipt", "sim_swap", "identity_shift", "liquidity_stress", "panic_sell"}:
            danger += 0.18
    signal_type = G.nodes[node].get("signal_type")
    if signal_type in {"identity_shift", "sim_swap_hint", "shared_signal_detected", "device_reset", "stress_signal"}:
        danger += 0.20
    return round(min(danger, 1.0), 3)


def trust_propagation_score(G: nx.Graph, node: str, max_depth: int = 2, beta: float = 0.65) -> float:
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


def relational_gravity(G: nx.Graph, node: str) -> float:
    if node not in G:
        return 0.0
    gravity = 0.0
    for other in G.nodes:
        if other == node:
            continue
        try:
            d = len(nx.shortest_path(G, node, other)) - 1
        except nx.NetworkXNoPath:
            continue
        trust = float(G.nodes[other].get("signal_severity", 0.0) or 0.0) + max(1, G.degree(other)) / 10.0
        gravity += trust / ((d + 1) ** 2)
    return round(gravity, 3)


def structure_similarity(G: nx.Graph, a: str, b: str) -> float:
    na = set(G.neighbors(a)) if a in G else set()
    nb = set(G.neighbors(b)) if b in G else set()
    union = len(na | nb)
    if union == 0:
        return 0.0
    return round(len(na & nb) / union, 3)


def path_similarity(events_df: pd.DataFrame, a: str, b: str) -> float:
    def sig(node: str):
        sub = events_df[events_df["source_id"].astype(str) == str(node)]
        return sub["event_type"].astype(str).tolist()[:6]
    sa, sb = sig(a), sig(b)
    if not sa and not sb:
        return 0.0
    m = max(len(sa), len(sb), 1)
    eq = sum(1 for i in range(min(len(sa), len(sb))) if sa[i] == sb[i])
    return round(eq / m, 3)


def pattern_match(events_df: pd.DataFrame, nodes: tuple[str, str]) -> float:
    labels = Counter(events_df[events_df["source_id"].astype(str).isin([str(nodes[0]), str(nodes[1])])]["label"].astype(str).tolist())
    suspicious = labels.get("mule_pattern", 0) + labels.get("scam_ring", 0) + labels.get("social_chain", 0) + labels.get("historical_stress", 0)
    total = max(sum(labels.values()), 1)
    return round(min(1.0, suspicious / total + (0.15 if suspicious else 0.0)), 3)


def shadow_coordination(events_df: pd.DataFrame, G: nx.Graph, top_n: int = 10) -> list[dict]:
    series = pulse_series(events_df)
    nodes = list(series.keys())[:60]
    results = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            a, b = nodes[i], nodes[j]
            direct = G.has_edge(a, b)
            sync = max(0.0, safe_corr(series[a], series[b]))
            struct = structure_similarity(G, a, b)
            path = path_similarity(events_df, a, b)
            patt = pattern_match(events_df, (a, b))
            score = round(0.35 * sync + 0.20 * struct + 0.20 * path + 0.25 * patt, 3)
            if score >= 0.55 and not direct:
                results.append({"a": a, "b": b, "sync": sync, "struct": struct, "path": path, "pattern": patt, "score": score})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


def entropy_analysis(events_df: pd.DataFrame) -> float:
    labels = events_df["event_type"].astype(str).value_counts(normalize=True)
    if labels.empty:
        return 0.0
    h = -sum(float(p) * math.log(float(p), 2) for p in labels.values if p > 0)
    return round(h, 3)


def criticality_score(events_df: pd.DataFrame) -> float:
    if len(events_df) == 0:
        return 0.0
    labels = events_df["label"].astype(str)
    abnormal = labels.isin(["mule_pattern", "scam_ring", "social_chain", "historical_stress"]).mean()
    burstiness = min(1.0, len(events_df) / 5000.0)
    return round(min(1.0, 0.55 * abnormal + 0.45 * burstiness), 3)


def morphogenesis_signature(events_df: pd.DataFrame) -> dict:
    labels = Counter(events_df["label"].astype(str).tolist())
    total = max(len(events_df), 1)
    abnormal_ratio = (labels.get("mule_pattern", 0) + labels.get("scam_ring", 0) + labels.get("social_chain", 0) + labels.get("historical_stress", 0)) / total
    bridge_proxy = len(events_df[events_df["target_id"].astype(str).str.startswith(("MULE_", "BAD_", "STRESS_"), na=False)])
    signature = min(1.0, abnormal_ratio * 1.8 + bridge_proxy / max(total, 1))
    return {"abnormal_ratio": round(abnormal_ratio, 3), "bridge_proxy": int(bridge_proxy), "morphogenetic_signature": round(signature, 3)}


def system_indices(G: nx.Graph, events_df: pd.DataFrame, shadow_pairs: list[dict], gravity_top: list[dict]) -> dict:
    ent = entropy_analysis(events_df)
    crit = criticality_score(events_df)
    sc_avg = round(sum(x["score"] for x in shadow_pairs) / max(len(shadow_pairs), 1), 3)
    grav_avg = round(sum(x["gravity"] for x in gravity_top) / max(len(gravity_top), 1), 3) if gravity_top else 0.0
    nhi = round(max(0.0, min(100.0, 100 - (ent * 12 + sc_avg * 35 + crit * 30))), 2)
    tpi = round(max(0.0, min(100.0, sc_avg * 45 + crit * 35 + ent * 10)), 2)
    scr = round(max(0.0, min(100.0, (100 - nhi) * 0.45 + tpi * 0.55 + grav_avg * 1.5)), 2)
    return {"entropy": ent, "criticality": crit, "NHI": nhi, "TPI": tpi, "SCR": scr}


def pre_contact_risk(node_metrics: dict, system_metrics: dict, pattern_match_score: float = 0.0) -> float:
    base = 100 * (0.25 * node_metrics.get("danger", 0.0) + 0.20 * min(node_metrics.get("gravity", 0.0) / 5.0, 1.0) + 0.20 * node_metrics.get("trust_risk", 0.0) + 0.15 * pattern_match_score + 0.20 * min(system_metrics.get("TPI", 0.0) / 100.0, 1.0))
    return round(min(100.0, base), 2)


def decision_from_risk(risk: float) -> str:
    if risk >= 75:
        return "BLOCK"
    if risk >= 45:
        return "REVIEW"
    return "ALLOW"
