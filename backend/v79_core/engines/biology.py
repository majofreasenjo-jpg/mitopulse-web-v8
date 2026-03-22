from __future__ import annotations
from backend.v79_core.core.helpers import clamp

class BiologyEngine:
    def compute(self, raw):
        sei = clamp(raw["energy_flow"])
        sdi = clamp(raw["homeostasis_loss"] * 0.55 + raw["structural_strain"] * 0.45)
        pmi = clamp(raw["mutation_pressure"])
        aes = clamp(raw["mutation_pressure"] * 0.55 + raw["identity_drift"] * 0.45)
        sai = clamp(raw["homeostasis_loss"] * 0.68 + raw["structural_strain"] * 0.32)
        iml = clamp(1 - raw["defense_activation"] * 0.5)
        iri = clamp(raw["defense_activation"])
        msi = clamp(raw["structural_strain"] * 0.52 + raw["homeostasis_loss"] * 0.48)
        sii = clamp(1 - raw["behavior_noise"] * 0.7)
        return {
            "sei": round(sei, 4),
            "sdi": round(sdi, 4),
            "pmi": round(pmi, 4),
            "aes": round(aes, 4),
            "sai": round(sai, 4),
            "iml": round(iml, 4),
            "iri": round(iri, 4),
            "msi": round(msi, 4),
            "sii": round(sii, 4),
        }
