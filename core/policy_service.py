import json
from pathlib import Path

POLICY_PATH = Path("config/action_policies.json")

def load_policies():
    if not POLICY_PATH.exists():
        return {}
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))

def save_policies(data):
    POLICY_PATH.parent.mkdir(parents=True, exist_ok=True)
    POLICY_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data

def get_policy(client_type: str):
    policies = load_policies()
    return policies.get(client_type, policies.get("generic", {}))
