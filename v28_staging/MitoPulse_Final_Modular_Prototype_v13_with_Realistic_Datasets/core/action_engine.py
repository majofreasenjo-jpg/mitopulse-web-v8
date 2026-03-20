from core.policy_service import get_policy

class ActionEngine:
    def decide(self, metrics, alerts, validated_alerts, client_type="generic"):
        scr = float(metrics.get("scr", 0) or 0)
        tpi = float(metrics.get("tpi", 0) or 0)
        mdi = float(metrics.get("mdi", 0) or 0)
        hidden = float(metrics.get("hidden_cluster_count", 0) or 0)

        decision = {
            "severity": "low",
            "action": "monitor",
            "confidence": 0.50,
            "policy": client_type,
            "explanation": [],
            "playbook_actions": []
        }

        if scr >= 75 or tpi >= 75:
            decision.update({"severity":"critical","action":"block_or_freeze","confidence":0.92})
            decision["explanation"].append("SCR/TPI critical threshold reached")
        elif scr >= 50 or mdi >= 55 or hidden >= 4:
            decision.update({"severity":"high","action":"review_and_limit","confidence":0.80})
            decision["explanation"].append("High distortion / hidden coordination detected")
        elif scr >= 25 or tpi >= 25:
            decision.update({"severity":"medium","action":"enhanced_monitoring","confidence":0.67})
            decision["explanation"].append("Early systemic pressure detected")
        else:
            decision["explanation"].append("No critical threshold exceeded")

        if len(validated_alerts) >= 3:
            decision["confidence"] = round(min(0.99, decision["confidence"] + 0.05), 2)
            decision["explanation"].append("Multiple Guardian-validated alerts")

        decision["playbook_actions"] = get_policy(client_type).get(decision["action"], [])
        return decision
