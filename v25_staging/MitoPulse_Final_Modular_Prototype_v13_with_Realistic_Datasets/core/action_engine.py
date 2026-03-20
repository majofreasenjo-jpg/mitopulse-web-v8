
import json, pathlib

class ActionEngine:
    def __init__(self):
        config_path = pathlib.Path("config/action_policies.json")
        if config_path.exists():
            self.policies = json.loads(config_path.read_text())
        else:
            self.policies = {}

    def decide(self, metrics, alerts, validated_alerts, client_type="generic"):
        scr = metrics.get("scr", 0)
        decision = {
            "severity": "low",
            "action": "monitor",
            "confidence": 0.5,
            "policy": client_type,
            "playbook_actions": []
        }

        if scr > 70:
            decision["action"] = "block_or_freeze"
            decision["severity"] = "critical"
            decision["confidence"] = 0.9

        decision["playbook_actions"] = self.policies.get(client_type, {}).get(
            decision["action"], []
        )
        return decision
