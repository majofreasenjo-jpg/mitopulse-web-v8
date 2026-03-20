def explain_result(result: dict) -> str:
    risk = result.get("risk")
    validation = result.get("validation")
    policy = result.get("policy")
    risk_state = getattr(risk, "risk_state", "UNKNOWN") if risk else "UNKNOWN"
    validated = getattr(validation, "validated", False) if validation else False
    policy_name = getattr(policy, "name", None) if policy else None
    return f"Protocol classified the case as {risk_state}; validation={'passed' if validated else 'not passed'}; policy={policy_name or 'none'}."
