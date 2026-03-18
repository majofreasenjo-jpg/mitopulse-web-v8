class NeuralResponseEngine:
    def detect_priority_paths(self, nodes):
        paths = []
        for n in nodes:
            score = float(n.get("score", 0) or 0)
            if score > 70:
                paths.append({
                    "entity": n["id"],
                    "priority": "high"
                })
        return paths
