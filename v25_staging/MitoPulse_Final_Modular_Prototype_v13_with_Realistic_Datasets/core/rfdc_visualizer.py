import pandas as pd
from collections import Counter

def build_graph_payload(events_df: pd.DataFrame, rfdc_result: dict) -> dict:
    nodes = {}
    links = []

    alerts_by_entity = {}
    for a in rfdc_result.get("alerts", []):
        ent = a.get("entity")
        if ent:
            alerts_by_entity.setdefault(ent, []).append(a)

    validated_entities = set()
    for a in rfdc_result.get("validated_alerts", []):
        ent = a.get("entity")
        if ent:
            validated_entities.add(ent)

    hidden_entities = set()
    for c in rfdc_result.get("hidden_clusters", []):
        for ent in c.get("entities", []):
            hidden_entities.add(str(ent))

    if not events_df.empty:
        for _, row in events_df.iterrows():
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

    # add inferred links for hidden clusters
    inferred = []
    for idx, c in enumerate(rfdc_result.get("hidden_clusters", [])[:20], start=1):
        ents = [str(x) for x in c.get("entities", [])[:8]]
        if len(ents) >= 2:
            for i in range(len(ents)-1):
                inferred.append({
                    "source": ents[i],
                    "target": ents[i+1],
                    "weight": c.get("size", 1),
                    "style": "dashed",
                    "inferred": True
                })

    metrics = rfdc_result.get("metrics", {})
    palette = {
        "stable": "#20c997",
        "anomaly": "#ffd166",
        "risk": "#ef476f",
        "hidden": "#7b61ff",
        "guardian": "#00bbf9",
        "neutral": "#adb5bd",
        "simulation": "#6c757d",
        "future": "#ffffff",
    }

    return {
        "nodes": list(nodes.values())[:300],
        "links": (links[:500] + inferred[:150]),
        "metrics": metrics,
        "palette": palette,
        "wave_summary": rfdc_result.get("wave_summary", {}),
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
