def map_v50_like_payload(payload: dict):
    return {
        "entity_id": payload.get("case_id", "v50_case"),
        "entity_type": payload.get("entity_type", "case_cluster"),
        "evidence_score": float(payload.get("evidence_score", 0.72)),
        "trust_score": float(payload.get("trust_score", 0.61)),
        "trust_velocity": float(payload.get("trust_velocity", 0.02)),
        "trust_volatility": float(payload.get("trust_volatility", 0.11)),
        "load_dev": float(payload.get("load_dev", 58.0)),
        "entropy_dev": float(payload.get("entropy_dev", 35.0)),
        "coordination_signal": float(payload.get("coordination_signal", 67.0)),
        "trust_break": float(payload.get("trust_break", 49.0)),
        "structural_distortion": float(payload.get("structural_distortion", 43.0)),
        "confidence": float(payload.get("confidence", 0.85)),
        "quorum_score": float(payload.get("quorum_score", 0.80)),
        "recovery_stability_score": float(payload.get("recovery_stability_score", 0.70)),
    }
