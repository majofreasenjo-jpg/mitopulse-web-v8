class ActionTriggerEngine:
    def detect_zones(self, nodes):
        zones = []
        for n in nodes:
            if float(n.get("score",0)) > 80:
                zones.append({
                    "entity": n["id"],
                    "trigger": "auto_action"
                })
        return zones
