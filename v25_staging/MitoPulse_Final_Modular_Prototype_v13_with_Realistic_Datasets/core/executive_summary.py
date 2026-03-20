def build_summary(metrics, decision, alerts):
    return {
        "system_state": metrics.get("band", "unknown"),
        "main_risk": metrics.get("message", ""),
        "severity": decision["severity"],
        "recommended_action": decision["action"],
        "confidence": decision["confidence"],
        "policy": decision.get("policy", "generic"),
        "alerts_count": len(alerts),
        "playbook_actions": decision.get("playbook_actions", []),
        "key_metrics": {
            "NHI": metrics.get("nhi"),
            "TPI": metrics.get("tpi"),
            "SCR": metrics.get("scr"),
            "MDI": metrics.get("mdi")
        },
        "top_explanations": decision.get("explanation", [])[:5]
    }
