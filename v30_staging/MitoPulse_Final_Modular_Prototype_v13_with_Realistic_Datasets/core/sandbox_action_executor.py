import json
from pathlib import Path
from datetime import datetime, timezone

class SandboxActionExecutor:
    def __init__(self, state_path="sandbox/sandbox_state.json"):
        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            self.state_path.write_text(json.dumps({
                "blocked_entities": [],
                "limited_entities": [],
                "events": []
            }, indent=2), encoding="utf-8")

    def _load(self):
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save(self, data):
        self.state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def execute(self, entity_id: str, action: str, reason: str = ""):
        state = self._load()
        ts = datetime.now(timezone.utc).isoformat()
        event = {
            "timestamp": ts,
            "entity_id": entity_id,
            "action": action,
            "reason": reason
        }

        if action == "block_or_freeze":
            if entity_id not in state["blocked_entities"]:
                state["blocked_entities"].append(entity_id)
        elif action == "review_and_limit":
            if entity_id not in state["limited_entities"]:
                state["limited_entities"].append(entity_id)

        state["events"].append(event)
        self._save(state)
        return {"status": "ok", "event": event, "state": state}
