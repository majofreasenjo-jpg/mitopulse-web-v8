from pathlib import Path
import json

BASE = Path(__file__).resolve().parent.parent
USERS = BASE / "data" / "users.json"

def login(username: str, password: str):
    data = json.loads(USERS.read_text(encoding="utf-8"))
    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            return {
                "status": "ok",
                "username": username,
                "role": user["role"],
                "tenant_id": user["tenant_id"]
            }
    return {"status": "fail"}
