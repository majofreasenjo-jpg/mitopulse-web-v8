import random

class RiskFieldEngine:
    def generate(self, nodes):
        field = []
        for n in nodes:
            field.append({
                "x": n.get("x", 0),
                "y": n.get("y", 0),
                "intensity": float(n.get("score", 0))/100
            })
        return field
