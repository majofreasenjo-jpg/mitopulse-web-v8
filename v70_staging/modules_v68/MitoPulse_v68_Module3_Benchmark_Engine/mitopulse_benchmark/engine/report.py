def build_report(metrics: dict) -> dict:
    return {
        "summary": {
            "lead_time": metrics["lead_time"],
            "precision": metrics["precision"],
            "fpr": metrics["fpr"],
            "fnr": metrics["fnr"],
            "loss_prevented": metrics["loss_prevented"],
            "sai": metrics["sai"]
        },
        "conclusion": "MitoPulse superior" if metrics["sai"] > 0 else "Baseline superior"
    }
