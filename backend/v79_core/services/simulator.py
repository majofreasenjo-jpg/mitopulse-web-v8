from __future__ import annotations
import math
import random

class RuntimeSignalSimulator:
    def __init__(self, seed=7):
        self.random = random.Random(seed)
        self.tick = 0
        self.raw_history = []

    def _n(self, amt=0.02):
        return self.random.uniform(-amt, amt)

    def next(self):
        self.tick += 1
        t = self.tick
        base = min(1.0, 0.08 + t * 0.0105)
        wave = 0.05 * math.sin(t / 3.5)

        raw = {
            "tick": t,
            "energy_flow": max(0.0, min(1.0, 0.88 - 0.22 * base + self._n())),
            "behavior_noise": max(0.0, min(1.0, 0.12 + 0.62 * base + wave + self._n())),
            "identity_drift": max(0.0, min(1.0, 0.10 + 0.70 * base + 0.03 * math.cos(t / 3.1) + self._n())),
            "relational_density": max(0.0, min(1.0, 0.28 + 0.46 * base + self._n())),
            "propagation_pressure": max(0.0, min(1.0, 0.11 + 0.78 * base + 0.04 * math.sin(t / 2.4) + self._n())),
            "structural_strain": max(0.0, min(1.0, 0.10 + 0.73 * base + self._n())),
            "homeostasis_loss": max(0.0, min(1.0, 0.07 + 0.68 * base + self._n())),
            "mutation_pressure": max(0.0, min(1.0, 0.10 + 0.66 * base + self._n())),
            "defense_activation": max(0.0, min(1.0, 0.08 + 0.42 * base + self._n())),
        }
        self.raw_history.append(raw)
        return raw

    def latest(self):
        return self.raw_history[-1] if self.raw_history else None

    def reset(self):
        self.tick = 0
        self.raw_history.clear()
