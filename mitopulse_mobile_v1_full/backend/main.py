import os, json, sqlite3, time
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from jinja2 import Template

DB_PATH = os.environ.get("MITOPULSE_DB", "./mitopulse.db")
ALLOWED_SKEW = int(os.environ.get("MITOPULSE_ALLOWED_SKEW_SECONDS", "86400"))
API_KEY = os.environ.get("MITOPULSE_API_KEY")  # optional

app = FastAPI(title="MitoPulse Backend Enterprise", version="1.0.0")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def now_ts() -> int:
    return int(time.time())

def init_db():
    conn = db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS identity_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL,
      device_id TEXT NOT NULL,
      ts INTEGER NOT NULL,
      request_id TEXT NOT NULL UNIQUE,
      dynamic_id TEXT NOT NULL,
      index_value REAL NOT NULL,
      slope REAL NOT NULL,
      tier TEXT NOT NULL,
      risk INTEGER NOT NULL,
      coercion INTEGER NOT NULL,
      meta_json TEXT NOT NULL,
      created_at INTEGER NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS verifications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL,
      device_id TEXT NOT NULL,
      ts INTEGER NOT NULL,
      request_id TEXT NOT NULL UNIQUE,
      dynamic_id TEXT NOT NULL,
      verified INTEGER NOT NULL,
      reason TEXT NOT NULL,
      created_at INTEGER NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      kind TEXT NOT NULL,
      user_id TEXT,
      device_id TEXT,
      request_id TEXT,
      detail TEXT NOT NULL,
      created_at INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

def require_api_key(x_api_key: Optional[str]):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid_api_key")

class IdentityEvent(BaseModel):
    user_id: str
    device_id: str
    ts: int
    request_id: str
    dynamic_id: str
    index_value: float = Field(..., ge=0.0, le=1.0)
    slope: float
    tier: str
    risk: int = Field(..., ge=0, le=100)
    coercion: bool
    meta: Dict[str, Any] = Field(default_factory=dict)

class VerifyRequest(BaseModel):
    user_id: str
    device_id: str
    ts: int
    request_id: str
    dynamic_id: str

@app.get("/health")
def health():
    return {"ok": True, "db": DB_PATH}

@app.post("/v1/identity-events")
def post_identity_event(evt: IdentityEvent, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    if abs(now_ts() - evt.ts) > ALLOWED_SKEW:
        conn = db()
        conn.execute("INSERT INTO audit_logs(kind,user_id,device_id,request_id,detail,created_at) VALUES (?,?,?,?,?,?)",
                     ("reject_time_skew", evt.user_id, evt.device_id, evt.request_id,
                      f"skew={abs(now_ts()-evt.ts)} allowed={ALLOWED_SKEW}", now_ts()))
        conn.commit(); conn.close()
        raise HTTPException(status_code=400, detail="timestamp_out_of_range")

    conn = db()
    try:
        conn.execute("""
        INSERT INTO identity_events(user_id,device_id,ts,request_id,dynamic_id,index_value,slope,tier,risk,coercion,meta_json,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (evt.user_id, evt.device_id, evt.ts, evt.request_id, evt.dynamic_id,
              float(evt.index_value), float(evt.slope), evt.tier, int(evt.risk), 1 if evt.coercion else 0,
              json.dumps(evt.meta, ensure_ascii=False), now_ts()))
        conn.execute("INSERT INTO audit_logs(kind,user_id,device_id,request_id,detail,created_at) VALUES (?,?,?,?,?,?)",
                     ("identity_event", evt.user_id, evt.device_id, evt.request_id, "accepted", now_ts()))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.execute("INSERT INTO audit_logs(kind,user_id,device_id,request_id,detail,created_at) VALUES (?,?,?,?,?,?)",
                     ("reject_replay_request_id", evt.user_id, evt.device_id, evt.request_id, "duplicate request_id", now_ts()))
        conn.commit(); conn.close()
        raise HTTPException(status_code=409, detail="replay_request_id")
    conn.close()
    return {"ok": True}

@app.post("/v1/verify")
def verify(req: VerifyRequest, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    conn = db()
    try:
        conn.execute("""
        INSERT INTO verifications(user_id,device_id,ts,request_id,dynamic_id,verified,reason,created_at)
        VALUES (?,?,?,?,?,?,?,?)
        """, (req.user_id, req.device_id, req.ts, req.request_id, req.dynamic_id, 0, "pending", now_ts()))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.execute("UPDATE verifications SET verified=?, reason=?, created_at=? WHERE request_id=?",
                     (0, "replay_request_id", now_ts(), req.request_id))
        conn.execute("INSERT INTO audit_logs(kind,user_id,device_id,request_id,detail,created_at) VALUES (?,?,?,?,?,?)",
                     ("reject_replay_request_id", req.user_id, req.device_id, req.request_id, "duplicate verify request_id", now_ts()))
        conn.commit(); conn.close()
        return {"verified": False, "reason": "replay_request_id"}

    row = conn.execute("""
        SELECT dynamic_id FROM identity_events
        WHERE user_id=? AND device_id=?
        ORDER BY ts DESC LIMIT 1
    """, (req.user_id, req.device_id)).fetchone()

    if not row:
        verified, reason = False, "no_identity_events"
    else:
        verified = (row["dynamic_id"] == req.dynamic_id)
        reason = "ok" if verified else "mismatch"

    conn.execute("UPDATE verifications SET verified=?, reason=?, created_at=? WHERE request_id=?",
                 (1 if verified else 0, reason, now_ts(), req.request_id))
    conn.execute("INSERT INTO audit_logs(kind,user_id,device_id,request_id,detail,created_at) VALUES (?,?,?,?,?,?)",
                 ("verify", req.user_id, req.device_id, req.request_id, reason, now_ts()))
    conn.commit(); conn.close()
    return {"verified": verified, "reason": reason}

DASH = Template("""
<!doctype html><html><head><meta charset="utf-8"/>
<title>MitoPulse Dashboard</title>
<style>
body{font-family:Arial;background:#0b0f14;color:#e6edf3;margin:24px}
a{color:#7dd3fc}
.card{background:#111827;border:1px solid #1f2937;border-radius:14px;padding:14px 16px;min-width:220px}
.top{display:flex;gap:16px;margin:12px 0 18px}
.num{font-size:34px;font-weight:700;margin-top:6px}
table{width:100%;border-collapse:collapse;margin-top:10px;background:#0f172a;border:1px solid #1f2937;border-radius:14px;overflow:hidden}
th,td{padding:10px;border-bottom:1px solid #1f2937;font-size:13px}
th{color:#9ca3af;font-weight:600;background:#0b1220;text-align:left}
.badge{display:inline-block;padding:4px 10px;border-radius:999px;font-size:12px}
.ok{background:#052e16;color:#86efac;border:1px solid #14532d}
.bad{background:#450a0a;color:#fca5a5;border:1px solid #7f1d1d}
.tier{background:#1f2937;color:#e5e7eb;border:1px solid #374151}
</style></head><body>
<h1 style="margin:0">MitoPulse Enterprise Dashboard</h1>
<div style="color:#9ca3af;margin-top:6px">DB: {{db}} | Skew: {{skew}}s | <a href="/docs">/docs</a></div>

<div class="top">
  <div class="card"><div style="color:#9ca3af;font-size:12px;letter-spacing:.08em">IDENTITY EVENTS</div><div class="num">{{stats.events}}</div></div>
  <div class="card"><div style="color:#9ca3af;font-size:12px;letter-spacing:.08em">VERIFICATIONS</div><div class="num">{{stats.verifications}}</div></div>
  <div class="card"><div style="color:#9ca3af;font-size:12px;letter-spacing:.08em">COERCION ALERTS</div><div class="num" style="color:#f87171">{{stats.coercions}}</div></div>
</div>

<h2>Latest Identity Events (derived only)</h2>
<table>
<tr><th>User</th><th>Device</th><th>ts</th><th>dynamic_id</th><th>index</th><th>slope</th><th>tier</th><th>risk</th><th>coercion</th></tr>
{% for r in events %}
<tr>
<td>{{r.user_id}}</td><td>{{r.device_id}}</td><td>{{r.ts}}</td>
<td style="font-family:ui-monospace,Menlo,monospace">{{r.dynamic_id[:12]}}…</td>
<td>{{"%.3f"|format(r.index_value)}}</td><td>{{"%.4f"|format(r.slope)}}</td>
<td><span class="badge tier">{{r.tier}}</span></td>
<td>{{r.risk}}</td>
<td>{% if r.coercion %}<span class="badge bad">⚠ COERCION</span>{% else %}<span class="badge ok">✓ OK</span>{% endif %}</td>
</tr>
{% endfor %}
</table>

<h2 style="margin-top:22px">Latest Verifications</h2>
<table>
<tr><th>User</th><th>Device</th><th>ts</th><th>dynamic_id</th><th>verified</th><th>reason</th><th>created_at</th></tr>
{% for r in verifications %}
<tr>
<td>{{r.user_id}}</td><td>{{r.device_id}}</td><td>{{r.ts}}</td>
<td style="font-family:ui-monospace,Menlo,monospace">{{r.dynamic_id[:12]}}…</td>
<td>{{r.verified}}</td><td>{{r.reason}}</td><td>{{r.created_at}}</td>
</tr>
{% endfor %}
</table>
</body></html>
""")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    conn = db()
    events = conn.execute("SELECT user_id,device_id,ts,dynamic_id,index_value,slope,tier,risk,coercion FROM identity_events ORDER BY ts DESC LIMIT 20").fetchall()
    verifs = conn.execute("SELECT user_id,device_id,ts,dynamic_id,verified,reason,created_at FROM verifications ORDER BY created_at DESC LIMIT 20").fetchall()
    stats = {
        "events": conn.execute("SELECT COUNT(*) c FROM identity_events").fetchone()["c"],
        "verifications": conn.execute("SELECT COUNT(*) c FROM verifications").fetchone()["c"],
        "coercions": conn.execute("SELECT COUNT(*) c FROM identity_events WHERE coercion=1").fetchone()["c"],
    }
    conn.close()
    return HTMLResponse(DASH.render(db=DB_PATH, skew=ALLOWED_SKEW, stats=stats, events=events, verifications=verifs))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
