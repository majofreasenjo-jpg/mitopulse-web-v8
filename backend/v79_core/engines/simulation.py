from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class SimulationEngine:
    def project(self, raw, steps=10):
        scale = 0.06 + 0.004 * min(steps, 24)
        projected = {}
        for k, v in raw.items():
            if k == "energy_flow":
                projected[k] = clamp(v - steps * 0.01)
            elif k == "tick":
                projected[k] = raw["tick"] + steps
            else:
                projected[k] = clamp(v + scale * (1 - v))
        return projected
