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

        decision["playbook_actions"] = self._policy_actions(client_type, decision["action"], decision["severity"])
        return decision

    def _policy_actions(self, client_type, action, severity):
        base = {
            "monitor": ["Log event", "Keep entity under observation"],
            "enhanced_monitoring": ["Increase monitoring window", "Raise analyst visibility"],
            "review_and_limit": ["Send to review queue", "Reduce limits / privileges"],
            "block_or_freeze": ["Block transaction / session", "Freeze entity / cluster", "Escalate to incident queue"],
        }
        policy_map = {
            "marketplace": {
                "monitor": ["Monitor seller activity", "Watch review velocity"],
                "enhanced_monitoring": ["Hold payouts", "Flag catalog changes"],
                "review_and_limit": ["Suspend promotions", "Limit listings", "Manual trust review"],
                "block_or_freeze": ["Freeze seller payouts", "Suspend account", "Isolate related accounts"],
            },
            "banking": {
                "monitor": ["Monitor account flows", "Extend AML observation"],
                "enhanced_monitoring": ["Require step-up auth", "Reduce transfer thresholds"],
                "review_and_limit": ["Send to AML/fraud ops", "Limit beneficiaries", "Hold suspicious transfers"],
                "block_or_freeze": ["Block transfer", "Freeze account", "Escalate to fraud/AML incident"],
            },
            "afp": {
                "monitor": ["Track concentration changes", "Watch liquidity stress"],
                "enhanced_monitoring": ["Run extra stress test", "Increase portfolio review cadence"],
                "review_and_limit": ["Limit exposure growth", "Escalate to risk committee"],
                "block_or_freeze": ["Trigger crisis protocol", "Freeze portfolio action under policy", "Escalate systemic alert"],
            },
            "crypto": {
                "monitor": ["Watch wallet cluster", "Track on-chain velocity"],
                "enhanced_monitoring": ["Increase transaction scrutiny", "Restrict withdrawal speed"],
                "review_and_limit": ["Hold withdrawals", "Require manual review"],
                "block_or_freeze": ["Freeze wallet/account", "Escalate to compliance", "Isolate related wallets"],
            }
        }
        policy = policy_map.get(client_type, {})
        return policy.get(action, base.get(action, []))
