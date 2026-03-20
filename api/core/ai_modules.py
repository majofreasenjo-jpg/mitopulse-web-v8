def semantic_ingestion_ai(raw):
    return {
        "normalized": True,
        "mapped_fields": ["entity_id","timestamp","value","kind"],
        "sample": raw[:2] if isinstance(raw, list) else raw
    }

def local_pattern_ai(entities):
    return {
        "anomalies": [e["id"] for e in entities if e.get("value", 0) >= 80],
        "labels": [{"id": e["id"], "label": "high_anomaly" if e.get("value",0)>=80 else "normal"} for e in entities]
    }

def behavioral_ai(entities):
    out = []
    for e in entities:
        v = e.get("value",0)
        profile = "cooperative"
        if v >= 90:
            profile = "predatory"
        elif v >= 75:
            profile = "opportunistic"
        out.append({"id": e["id"], "behavioral_profile": profile})
    return out

def evolution_ai():
    return {
        "mutations": [
            {"pattern_id":"mut_01","type":"coordination_shift","risk_score":82},
            {"pattern_id":"mut_02","type":"wave_amplification","risk_score":77},
        ]
    }

def explainability_ai(summary):
    return {
        "executive_text": f"MitoPulse detects elevated systemic risk. Main signal: {summary.get('top_risk','unknown')}.",
        "technical_text": "RFDC and companion modules indicate rising pressure, anomaly concentration and action relevance."
    }

def strategy_copilot(summary):
    return {
        "recommended_action": summary.get("recommended_action","enhanced_monitoring"),
        "alternative_actions": ["enhanced_monitoring","review_and_limit","block_or_freeze"]
    }
