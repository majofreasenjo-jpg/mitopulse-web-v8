
import random

class FraudEvolutionEngine:

    def generate_pattern(self):
        return {
            "type": random.choice(["spoofing","wash_trading","coordination"]),
            "intensity": random.uniform(0.1,1.0)
        }

    def mutate_pattern(self, pattern):
        pattern["intensity"] *= random.uniform(0.8,1.2)
        return pattern
