class WaveImpactEngine:
    def apply(self, nodes, waves):
        impacted = []
        for n in nodes:
            score = float(n.get("score", 0) or 0)
            for w in waves:
                if w["entity"] != n["id"]:
                    score += w["intensity"] * 10
            n["score"] = min(100, score)
            impacted.append(n)
        return impacted
