import time
import uuid
from typing import Dict, List


def build_federated_audit(entity_id: str, action: str, votes: List[Dict], quorum_result: Dict) -> Dict:
    return {
        "audit_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "entity_id": entity_id,
        "action": action,
        "votes": votes,
        "quorum_result": quorum_result,
    }
