import random

class WaveEngineVisual:
    def propagate(self, nodes):
        waves = []
        for n in nodes:
            score = float(n.get("score", 0) or 0)
            if score > 40:
                waves.append({
                    "entity": n["id"],
                    "intensity": score / 100,
                    "direction": random.choice(["outward","inward"]),
                    "speed": round(random.uniform(0.5,2.0),2)
                })
        return waves
