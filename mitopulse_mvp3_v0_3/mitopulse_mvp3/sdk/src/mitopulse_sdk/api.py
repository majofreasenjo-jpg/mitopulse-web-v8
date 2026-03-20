from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Dict

from .engine import Sample, MitoPulseEngine


def _to_b64_secret(secret: str) -> str:
    return base64.b64encode(secret.encode("utf-8")).decode("ascii")


@dataclass
class LocalIdentityEngine:
    """Convenience wrapper: returns a stable dict schema for the MVP."""

    secret: str
    window_days: int = 60

    def __post_init__(self) -> None:
        self._engine = MitoPulseEngine(_to_b64_secret(self.secret))
        self._engine.window_days = int(self.window_days)

    def process(self, sample: Sample) -> Dict:
        r = self._engine.process(sample)
        vec = r["vector"]
        return {
            "mitopulse_index": float(r["index"]),
            "slope": float(vec.get("slope", 0.0)),
            "vector": vec,
            "tier": r["tier_used"],
            "dynamic_id": r["dynamic_id"],
        }
