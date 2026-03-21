import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.mitopulse_protocol.core.trust_engine import TrustEngine

def trust_score(propagation_data: dict):
    # Using the native protocol Trust Engine to process the risk propagation state
    engine = TrustEngine()
    
    # Derive trust degradation from the Structural Compromise Ratio (SCR)
    scr = propagation_data.get("scr", 0) / 100.0
    base_trust = max(0.01, 1.0 - (scr * 1.5))
    volatility = scr * 0.4
    velocity = -scr * 0.2
    
    profile = engine.compute("ENT-LIVE-01", base_trust, velocity, volatility)
    
    return {
        "entity_id": profile.entity_id,
        "base_trust": profile.trust_score,
        "velocity": profile.trust_velocity,
        "volatility": profile.trust_volatility,
        "reserve_buffer": profile.trust_reserve,
        "machine_state": profile.trust_state
    }
