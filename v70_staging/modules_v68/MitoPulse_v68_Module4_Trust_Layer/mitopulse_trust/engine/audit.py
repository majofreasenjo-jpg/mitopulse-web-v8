
import uuid
import time

def create_audit_entry(entity, decision, explanation):
    return {
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "entity": entity,
        "decision": decision,
        "explanation": explanation
    }
