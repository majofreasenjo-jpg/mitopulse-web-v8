from __future__ import annotations
from pathlib import Path
import json
import yaml
from engine.graph_builder import build_graph
from ingestion.client_data_loader import load_client_folder, dataset_profile
from engine.core_engines import (
    relational_identity_score, cross_pulse_pairs, danger_signal_score, trust_propagation_score,
    relational_gravity, shadow_coordination, morphogenesis_signature, system_indices,
    pre_contact_risk, decision_from_risk
)
from engine.bioinspired_engine import extract_topology

BASE_DIR = Path(__file__).resolve().parents[1]


def load_profile(profile_name: str) -> dict:
    path = BASE_DIR / "profiles" / f"{profile_name}.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_historical_scenario(name: str) -> dict:
    path = BASE_DIR / "historical" / f"{name}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def top_node_scores(G, events_df, limit: int = 12):
    rows = []
    for node, attrs in G.nodes(data=True):
        if attrs.get("node_type") != "customer":
            continue
        ri = relational_identity_score(G, node)
        ds = danger_signal_score(G, node)
        tp = trust_propagation_score(G, node)
        rg = relational_gravity(G, node)
        rows.append({"node": node, "relational_identity": ri, "danger": ds, "trust_risk": tp, "gravity": rg})
    rows.sort(key=lambda x: (x["danger"], x["gravity"], x["trust_risk"]), reverse=True)
    return rows[:limit]


def run_live_profile(profile_name: str) -> dict:
    profile = load_profile(profile_name)
    ds_path = BASE_DIR / profile["dataset"]
    customers, devices, events, signals = load_client_folder(str(ds_path))
    G = build_graph(customers, devices, events, signals)
    dp = dataset_profile(customers, devices, events, signals)

    cpairs = cross_pulse_pairs(events)
    shadow = shadow_coordination(events, G)
    top_nodes = top_node_scores(G, events)
    morph = morphogenesis_signature(events)
    system = system_indices(G, events, shadow, top_nodes)

    cluster_pattern = max([x["pattern"] for x in shadow], default=0.0)
    if top_nodes:
        top_nodes = [
            {**n, "PCR": pre_contact_risk(n, system, cluster_pattern), "decision": decision_from_risk(pre_contact_risk(n, system, cluster_pattern))}
            for n in top_nodes
        ]

    active_modules = [k for k, v in profile.get("modules", {}).items() if v]

    storyline = [
        "La red se carga y se construye la identidad relacional.",
        "Pulse y Cross-Pulse buscan sincronía operativa.",
        "Relational Gravity identifica centros de influencia.",
        "Shadow Coordination detecta coordinación sin enlaces directos.",
        "NHI, TPI y SCR resumen la salud y presión del ecosistema.",
        "Pre-Contact Risk emite la decisión preventiva.",
    ]

    return {
        "kind": "profile",
        "profile": profile,
        "dataset_profile": dp,
        "graph_stats": {"nodes": G.number_of_nodes(), "edges": G.number_of_edges()},
        "active_modules": active_modules,
        "topology": extract_topology(G),
        "top_nodes": top_nodes,
        "cross_pulse_pairs": cpairs,
        "shadow_pairs": shadow,
        "morphogenesis": morph,
        "system_indices": system,
        "storyline": storyline,
    }


def run_historical(name: str) -> dict:
    scenario = load_historical_scenario(name)
    return {
        "kind": "historical",
        "scenario": scenario,
        "active_modules": scenario.get("modules", []),
        "storyline": scenario.get("storyline", []),
        "windows": scenario.get("windows", []),
        "conclusion": scenario.get("conclusion", ""),
    }
