import math
import random

class GraphPhysicsEngine:
    def apply(self, nodes):
        updated = []
        for n in nodes:
            x = float(n.get("x", 0))
            y = float(n.get("y", 0))
            score = float(n.get("score", 0) or 0)

            # gravity pull to center
            cx, cy = 460, 210
            dx = (cx - x) * 0.01
            dy = (cy - y) * 0.01

            # vortex rotation
            angle = random.uniform(-0.1, 0.1)
            rx = x * math.cos(angle) - y * math.sin(angle)
            ry = x * math.sin(angle) + y * math.cos(angle)

            # score amplifies movement
            factor = 1 + (score / 100)

            updated.append({
                **n,
                "x": rx + dx * factor,
                "y": ry + dy * factor
            })
        return updated
