import sys
from pathlib import Path
from dataclasses import asdict, is_dataclass
from pprint import pprint
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages"))
from mitopulse_protocol.core.protocol_engine import ProtocolEngine
engine = ProtocolEngine()
payload = {
    "entity_id":"v62_demo_cluster",
    "entity_type":"wallet_cluster",
    "evidence_score":0.91,
    "trust_score":0.22,
    "trust_velocity":-0.03,
    "trust_volatility":0.21,
    "load_dev":73,
    "entropy_dev":49,
    "coordination_signal":82,
    "trust_break":61,
    "structural_distortion":56,
    "confidence":0.91,
    "quorum_score":0.87,
    "recovery_stability_score":0.55
}
result = engine.evaluate(payload)
for k,v in result.items():
    print("\n["+k.upper()+"]")
    if v is None:
        print(None)
    elif is_dataclass(v):
        pprint(asdict(v))
    else:
        pprint(v)
