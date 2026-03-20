import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages"))
from mitopulse_protocol.core.protocol_engine import ProtocolEngine

def main():
    engine = ProtocolEngine()
    result = engine.evaluate({
        "entity_id":"test_v54",
        "entity_type":"wallet",
        "evidence_score":0.86,
        "trust_score":0.71,
        "trust_velocity":0.03,
        "trust_volatility":0.08,
        "load_dev":60,
        "entropy_dev":36,
        "coordination_signal":67,
        "trust_break":49,
        "structural_distortion":45,
        "confidence":0.86,
        "quorum_score":0.82,
        "recovery_stability_score":0.73
    })
    assert result["validation"].validated is True
    assert result["policy"] is not None
    assert result["evaluation_id"] is not None
    print("Smoke OK")

if __name__ == "__main__":
    main()
