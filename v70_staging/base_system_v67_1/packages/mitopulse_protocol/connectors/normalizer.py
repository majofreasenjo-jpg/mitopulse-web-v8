def normalize_event(source: str, payload: dict) -> dict:
    return {
        "source": source,
        "entity_id": payload.get("entity_id") or payload.get("symbol") or payload.get("case_id") or "unknown_entity",
        "entity_type": payload.get("entity_type", source),
        "evidence_score": float(payload.get("evidence_score", 0.55)),
        "trust_score": float(payload.get("trust_score", 0.55)),
        "trust_velocity": float(payload.get("trust_velocity", 0.00)),
        "trust_volatility": float(payload.get("trust_volatility", 0.10)),
        "load_dev": float(payload.get("load_dev", 50.0)),
        "entropy_dev": float(payload.get("entropy_dev", 35.0)),
        "coordination_signal": float(payload.get("coordination_signal", 45.0)),
        "trust_break": float(payload.get("trust_break", 25.0)),
        "structural_distortion": float(payload.get("structural_distortion", 30.0)),
        "confidence": float(payload.get("confidence", 0.80)),
        "quorum_score": float(payload.get("quorum_score", 0.75)),
        "recovery_stability_score": float(payload.get("recovery_stability_score", 0.65)),
    }
