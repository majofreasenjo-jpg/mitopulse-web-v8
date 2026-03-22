from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class BaselineEngine:
    def compute(self, raw):
        sb = clamp(1 - raw["relational_density"] * 0.25)
        eb = clamp(raw["energy_flow"])
        lb = clamp(raw["structural_strain"])
        bb = clamp(raw["behavior_noise"])
        eb2 = clamp(raw["mutation_pressure"] * 0.7 + raw["behavior_noise"] * 0.3)
        metabolic_load = clamp(0.5 * lb + 0.3 * bb + 0.2 * eb2)
        return {
            "SB": round(sb, 4),
            "EB": round(eb, 4),
            "LB": round(lb, 4),
            "BB": round(bb, 4),
            "EB2": round(eb2, 4),
            "metabolic_load": round(metabolic_load, 4),
        }
