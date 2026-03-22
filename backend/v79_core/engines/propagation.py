from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class PropagationEngine:
    def compute(self, raw):
        wave = clamp(raw["propagation_pressure"])
        contagion = clamp(raw["propagation_pressure"] * 0.68 + raw["relational_density"] * 0.32)
        climate = clamp(raw["propagation_pressure"] * 0.45 + raw["structural_strain"] * 0.55)
        vortex = clamp(raw["propagation_pressure"] * 0.50 + raw["mutation_pressure"] * 0.50)
        return {
            "wave_intensity": round(wave, 4),
            "contagion_level": round(contagion, 4),
            "climate_instability": round(climate, 4),
            "vortex_formation": round(vortex, 4),
        }
