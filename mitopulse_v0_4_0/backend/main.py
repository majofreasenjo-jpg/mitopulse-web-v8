
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3, time, hashlib, hmac, base64, os

app = FastAPI()

DB_PATH = os.getenv("MITOPULSE_DB_PATH", "mitopulse.db")
ALLOWED_SKEW = int(os.getenv("MITOPULSE_ALLOWED_SKEW_SECONDS", "60"))

conn = sqlite3.connect(DB_PATH, check_same_thread=False)

conn.execute('''
CREATE TABLE IF NOT EXISTS identity_events (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id TEXT,
device_id TEXT,
ts INTEGER,
dynamic_id TEXT,
tier TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS audit_logs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
event_type TEXT,
user_id TEXT,
device_id TEXT,
verified INTEGER,
reason TEXT,
created_at INTEGER
)
''')

class IdentityEvent(BaseModel):
    user_id: str
    device_id: str
    ts: int
    dynamic_id: str
    signature: str
    tier: str

SECRET = os.getenv("MITOPULSE_SERVER_SECRET", "server_secret").encode()

def validate_signature(e: IdentityEvent):
    payload = f"{e.user_id}:{e.device_id}:{e.ts}:{e.dynamic_id}".encode()
    mac = hmac.new(SECRET, payload, hashlib.sha256).digest()
    expected = base64.urlsafe_b64encode(mac).decode().rstrip("=")
    return hmac.compare_digest(expected, e.signature)

@app.post("/v1/identity-events")
def post_identity(e: IdentityEvent):
    if not validate_signature(e):
        raise HTTPException(status_code=401, detail="invalid_signature")

    now = int(time.time())
    if abs(now - e.ts) > ALLOWED_SKEW:
        raise HTTPException(status_code=401, detail="expired")

    conn.execute("INSERT INTO identity_events (user_id,device_id,ts,dynamic_id,tier) VALUES (?,?,?,?,?)",
                 (e.user_id, e.device_id, e.ts, e.dynamic_id, e.tier))
    conn.commit()
    return {"status": "ok"}

@app.post("/v1/verify")
def verify(e: IdentityEvent):
    cur = conn.execute("SELECT dynamic_id FROM identity_events WHERE user_id=? AND device_id=? ORDER BY ts DESC LIMIT 1",
                       (e.user_id, e.device_id))
    row = cur.fetchone()
    verified = row and row[0] == e.dynamic_id

    conn.execute("INSERT INTO audit_logs (event_type,user_id,device_id,verified,reason,created_at) VALUES (?,?,?,?,?,?)",
                 ("verify", e.user_id, e.device_id, int(bool(verified)), "ok" if verified else "mismatch", int(time.time())))
    conn.commit()

    return {"verified": bool(verified)}
