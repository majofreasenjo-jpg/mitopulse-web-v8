import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])) # Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2])) # Add root to path

from backend.mitopulse_protocol.core.risk_engine import RiskEngine

def propagate(signal: float):
    # Authentic calculation: mapping the raw signal into a full RiskProfile
    engine = RiskEngine()
    
    # Simulating standard market deviations based on the signal strength
    load_dev = signal * 12.5
    entropy_dev = signal * 8.0
    coordination = signal * 40.0
    trust_break = signal * 5.0
    distortion = signal * 15.0
    
    profile = engine.assess(load_dev, entropy_dev, coordination, trust_break, distortion)
    
    return {
        "nhi": profile.nhi,
        "tpi": profile.tpi,
        "scr": profile.scr,
        "mdi": profile.mdi,
        "state": profile.state
    }
