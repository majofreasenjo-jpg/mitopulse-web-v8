import random

class LearningLoop:
    def generate_mutations(self):
        patterns = []
        for i in range(3):
            patterns.append({
                "pattern_id": f"mut_{i}",
                "type": random.choice(["wash_trading","coordination","burst_activity"]),
                "risk_score": random.randint(40,90)
            })
        return patterns
