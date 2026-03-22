def detect_local_pattern(payload: dict) -> dict:
    risk_hint = "predatory" if float(payload.get("coordination_signal", 0)) > 65 else "normal_variation"
    return {"pattern_hint": risk_hint, "reason": "based on local coordination and trust-break features"}
