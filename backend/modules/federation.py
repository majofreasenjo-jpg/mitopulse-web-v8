import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.mitopulse_protocol.validation.quorum import compute_quorum

def quorum(trust_data: dict, propagation_data: dict):
    # Assemble synthetic node votes derived from the risk and trust vectors
    votes = []
    
    # Node 1: Primary Oracle (Focuses on Trust State)
    v1 = "approve" if trust_data.get("base_trust", 0) > 0.4 else "reject"
    votes.append({"anchor_id": "ORCL-01", "vote": v1, "confidence": trust_data.get("base_trust")})
    
    # Node 2: Risk Monitor (Focuses on Structural Compression)
    v2 = "approve" if propagation_data.get("scr", 0) < 65 else "reject"
    votes.append({"anchor_id": "RSK-02", "vote": v2, "confidence": 0.85})
    
    # Node 3: Reserve Capacitor
    reserve = trust_data.get("reserve_buffer", 0)
    v3 = "approve" if reserve > 0.1 else "reject"
    votes.append({"anchor_id": "CAP-03", "vote": v3, "confidence": 0.75})
    
    score, is_approved = compute_quorum(votes)
    
    return {
        "consensus_score": score,
        "is_approved": is_approved,
        "federation_votes": len(votes),
        "quorum_met": True if score >= 0.70 else False
    }
