import json
from pathlib import Path
from datetime import datetime

WEBHOOK_LOG = Path("sandbox/webhook_log.json")

def send_webhook(payload):
    WEBHOOK_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not WEBHOOK_LOG.exists():
        WEBHOOK_LOG.write_text("[]", encoding="utf-8")

    data = json.loads(WEBHOOK_LOG.read_text(encoding="utf-8"))
    data.append({
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload
    })
    WEBHOOK_LOG.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"status": "sent", "payload": payload}
