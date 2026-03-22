from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class QuantumEngine:
    def compute(self, raw):
        legacy_exposure = clamp(raw["mutation_pressure"] * 0.35 + raw["identity_drift"] * 0.15)
        agility = clamp(1 - legacy_exposure * 0.7)
        if agility > 0.85:
            state = "pq-ready"
        elif agility > 0.65:
            state = "hybrid-secure"
        elif agility > 0.45:
            state = "transition-ready"
        else:
            state = "legacy-exposed"
        return {
            "quantum_legacy_exposure": round(legacy_exposure, 4),
            "crypto_agility_score": round(agility, 4),
            "crypto_state": state,
        }
