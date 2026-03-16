
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()
conn = sqlite3.connect("mitopulse.db", check_same_thread=False)
conn.execute('''
CREATE TABLE IF NOT EXISTS identity_events (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id TEXT,
device_id TEXT,
ts INTEGER,
dynamic_id TEXT
)
''')

class IdentityEvent(BaseModel):
    user_id:str
    device_id:str
    ts:int
    dynamic_id:str

@app.post("/v1/identity-events")
def post_event(e:IdentityEvent):
    conn.execute("INSERT INTO identity_events (user_id,device_id,ts,dynamic_id) VALUES (?,?,?,?)",
                 (e.user_id,e.device_id,e.ts,e.dynamic_id))
    conn.commit()
    return {"status":"ok"}

@app.post("/v1/verify")
def verify(e:IdentityEvent):
    cur = conn.execute("SELECT dynamic_id FROM identity_events WHERE user_id=? AND device_id=? ORDER BY ts DESC LIMIT 1",
                       (e.user_id,e.device_id))
    row = cur.fetchone()
    if row and row[0]==e.dynamic_id:
        return {"verified":True}
    return {"verified":False}
