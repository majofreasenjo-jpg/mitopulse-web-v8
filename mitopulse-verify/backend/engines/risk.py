import random
from typing import Dict, Any

class RiskEngine:
    """
    Evaluates behavioral and contextual factors to detect coercion,
    bot activity, or baseline drift in real-time.
    """
    def __init__(self):
        # In production, this would load historical baseline data for the device
        # from Redis or a Graph Database.
        pass

    def evaluate_risk(self, device_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculates a risk score from 0 (Safe) to 100 (High Risk).
        Returns the score and a classification level.
        """
        # --- MOCK DEMO BEHAVIOR ---
        # Simulate a complex stochastic analysis.
        # In reality, this checks telemetry (gyroscope, typing speed anomalies, IP jumping).
        
        base_risk = random.uniform(2.0, 15.0) # Nominal organic risk
        
        # If the context suggests a high-value transaction without historical precedent:
        if context and context.get("tx_amount", 0) > 10000:
            base_risk += 40.0
            
        # Example condition: If device ID is unknown or suspicious format
        if not device_id.startswith("node_"):
            base_risk += 80.0

        score = min(base_risk, 100.0)
        
        # Classify the risk
        if score < 20:
            level = "LOW"
        elif score < 60:
            level = "MEDIUM"
        else:
            level = "CRITICAL"

        return {
            "risk_score": round(score, 2),
            "level": level,
            "flags": ["large_transaction"] if score > 40 else []
        }
