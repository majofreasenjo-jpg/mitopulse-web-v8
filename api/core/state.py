from pathlib import Path
import json
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent.parent
STATE = BASE / "data" / "state.json"

def load_state():
    return json.loads(STATE.read_text(encoding="utf-8"))

def save_state(data):
    STATE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def append_audit(event_type: str, payload: dict):
    data = load_state()
    data["audit"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload
    })
    save_state(data)
    return data["audit"][-1]
