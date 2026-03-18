import math
from core.graph_physics_engine import GraphPhysicsEngine
from core.wave_engine_visual import WaveEngineVisual
from core.wave_impact_engine import WaveImpactEngine
from core.risk_field_engine import RiskFieldEngine
from core.neural_response_engine import NeuralResponseEngine
from core.action_trigger_engine import ActionTriggerEngine
import pandas as pd

def _spring_positions(node_ids, center=(460,210), base_radius=120):
    positions = {}
    n = max(1, len(node_ids))
    for i, node_id in enumerate(node_ids):
        angle = (2 * math.pi * i) / n
        ring = 1 + (i // 12)
        radius = base_radius + (ring-1) * 70
        x = center[0] + math.cos(angle) * radius
        y = center[1] + math.sin(angle) * radius
        positions[str(node_id)] = {"x": round(x,2), "y": round(y,2)}
    return positions

def build_graph_payload(events_df: pd.DataFrame, rfdc_result: dict) -> dict:
    nodes = {}
    links = []
    alerts_by_entity = {}
    for a in rfdc_result.get("alerts", []):
        ent = a.get("entity")
        if ent:
            alerts_by_entity.setdefault(str(ent), []).append(a)

    validated_entities = {str(a.get("entity")) for a in rfdc_result.get("validated_alerts", []) if a.get("entity")}
    hidden_entities = set()
    for c in rfdc_result.get("hidden_clusters", []):
        for ent in c.get("entities", []):
            hidden_entities.add(str(ent))

    if not events_df.empty:
        trimmed = events_df.tail(180).copy()
        for _, row in trimmed.iterrows():
            s = str(row.get("source_id", "UNKNOWN"))
            t = str(row.get("target_id", "UNKNOWN"))
            amount = float(row.get("amount", 0) or 0)
            for ent in [s, t]:
                if ent not in nodes:
                    role = "neutral"
                    if ent in hidden_entities:
                        role = "hidden_cluster"
                    if ent in validated_entities:
                        role = "guardian_validated"
                    if ent in alerts_by_entity:
                        role = "alert"
                    nodes[ent] = {
                        "id": ent,
                        "label": ent,
                        "role": role,
                        "score": max([float(x.get("score", 0) or 0) for x in alerts_by_entity.get(ent, [])], default=0),
                    }
            links.append({
                "source": s,
                "target": t,
                "weight": round(amount, 2),
                "style": "solid" if s != t else "loop"
            })

    # inferred links from hidden clusters
    inferred = []
    for c in rfdc_result.get("hidden_clusters", [])[:20]:
        ents = [str(x) for x in c.get("entities", [])[:8]]
        for i in range(len(ents)-1):
            inferred.append({
                "source": ents[i],
                "target": ents[i+1],
                "weight": c.get("size", 1),
                "style": "dashed",
                "inferred": True
            })

    node_list = list(nodes.values())[:40]
    positions = _spring_positions([n["id"] for n in node_list])

    palette = {
        "stable": "#20c997",
        "anomaly": "#ffd166",
        "risk": "#ef476f",
        "hidden": "#7b61ff",
        "guardian": "#00bbf9",
        "neutral": "#adb5bd",
        "simulation": "#6c757d",
        "future": "#ffffff",
        "wave": "#4cc9f0"
    }

    # wave centers based on top alert nodes
    wave_centers = []
    for n in node_list:
        if n["id"] in positions and n["role"] in ["alert", "hidden_cluster", "guardian_validated"]:
            wave_centers.append({
                "entity": n["id"],
                "x": positions[n["id"]]["x"],
                "y": positions[n["id"]]["y"],
                "strength": round(min(1.0, float(n.get("score", 0))/100.0 if n.get("score", 0) else 0.35), 3)
            })

    for n in node_list:
        if n["id"] in positions:
            n.update(positions[n["id"]])

    physics = GraphPhysicsEngine()
    node_list = physics.apply(node_list)

    wave_engine = WaveEngineVisual()
    dynamic_waves = wave_engine.propagate(node_list)

    impact_engine = WaveImpactEngine()
    node_list = impact_engine.apply(node_list, dynamic_waves)

    field_engine = RiskFieldEngine()
    risk_field = field_engine.generate(node_list)

    neural = NeuralResponseEngine()
    priority_paths = neural.detect_priority_paths(node_list)

    trigger_engine = ActionTriggerEngine()
    trigger_zones = trigger_engine.detect_zones(node_list)

    return {
        "nodes": node_list,
        "links": (links[:240] + inferred[:80]),
        "metrics": rfdc_result.get("metrics", {}),
        "palette": palette,
        "wave_summary": rfdc_result.get("wave_summary", {}),
        "wave_centers": wave_centers[:8],
        "dynamic_waves": dynamic_waves,
        "risk_field": risk_field,
        "priority_paths": priority_paths,
        "trigger_zones": trigger_zones,
    }

def build_demo_story(demo_id: str, rfdc_result: dict) -> dict:
    metrics = rfdc_result.get("metrics", {})
    if demo_id == "invisible_network":
        return {
            "title": "The Invisible Network",
            "subtitle": "Detectar coordinación oculta en una red aparentemente normal",
            "steps": [
                "Ecosistema aparentemente normal",
                "Aparecen micro-sincronizaciones",
                "Relational Dark Matter + MDI revelan distorsión",
                "Shadow Coordination infiere cluster oculto",
                "Guardian Swarm valida la amenaza"
            ],
            "headline": f"MDI={metrics.get('mdi', 0)} · Hidden clusters={len(rfdc_result.get('hidden_clusters', []))}"
        }
    if demo_id == "invisible_storm":
        return {
            "title": "The Invisible Storm",
            "subtitle": "Pequeñas anomalías evolucionan en una tormenta relacional",
            "steps": [
                "Aparecen señales débiles",
                "Las ondas relacionales se amplifican",
                "El contagio aumenta la presión del ecosistema",
                "TPI y SCR suben antes del evento crítico",
                "La defensa reduce la propagación"
            ],
            "headline": f"Waves={rfdc_result.get('wave_summary', {}).get('count', 0)} · SCR={metrics.get('scr', 0)}"
        }

    return {
        "title": "The Coming Collapse",
        "subtitle": "Detectar una crisis antes de que el mercado la vea",
        "steps": [
            "Mercado aparentemente estable",
            "Se acumula presión sistémica",
            "Criticality y Climate Pressure aumentan",
            "El sistema entra en zona de tipping point",
            "Financial collapse risk se vuelve visible"
        ],
        "headline": f"NHI={metrics.get('nhi', 0)} · TPI={metrics.get('tpi', 0)} · SCR={metrics.get('scr', 0)}"
    }
