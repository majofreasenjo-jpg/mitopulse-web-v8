def recommend_next_step(result: dict) -> str:
    risk = result.get("risk")
    risk_state = getattr(risk, "risk_state", "UNKNOWN") if risk else "UNKNOWN"
    if risk_state in {"CRITICAL", "COLLAPSE"}:
        return "Escalate to human review, freeze or isolate target, and inspect adjacent relational field."
    if risk_state == "INSTABILITY":
        return "Increase monitoring, raise challenge window sensitivity, and prepare containment policy."
    return "Continue monitoring under baseline thresholds."
