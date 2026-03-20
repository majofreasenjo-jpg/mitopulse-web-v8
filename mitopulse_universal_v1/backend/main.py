from __future__ import annotations
import os, hmac, hashlib, json, time
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3

DB_PATH = os.getenv("MITOPULSE_DB", "mitopulse.db")
ALLOWED_SKEW_SECONDS = int(os.getenv("MITOPULSE_ALLOWED_SKEW_SECONDS", "86400"))  # demo default 24h
API_KEY = os.getenv("MITOPULSE_API_KEY")  # optional

app = FastAPI(title="MitoPulse Enterprise Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS identity_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER NOT NULL,
        user_id TEXT NOT NULL,
        device_id TEXT NOT NULL,
        request_id TEXT NOT NULL UNIQUE,
        tier_used TEXT NOT NULL,
        index_value REAL NOT NULL,
        slope REAL NOT NULL,
        dynamic_id TEXT NOT NULL,
        risk INTEGER NOT NULL,
        coercion INTEGER NOT NULL,
        signature TEXT,
        created_at INTEGER NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER NOT NULL,
        user_id TEXT,
        device_id TEXT,
        request_id TEXT,
        action TEXT NOT NULL,
        ok INTEGER NOT NULL,
        reason TEXT,
        created_at INTEGER NOT NULL
    );
    """)
    con.commit()
    con.close()

init_db()

class IdentityEvent(BaseModel):
    ts: int
    user_id: str
    device_id: str
    request_id: str
    tier_used: str
    index: float = Field(..., alias="index_value")
    slope: float
    dynamic_id: str
    risk: int = 0
    coercion: bool = False
    signature: Optional[str] = None

class VerifyRequest(BaseModel):
    user_id: str
    device_id: str
    request_id: str
    dynamic_id: str

def audit(action: str, ok: bool, reason: str|None, user_id: str|None=None, device_id: str|None=None, request_id: str|None=None):
    con = db()
    con.execute(
        "INSERT INTO audit_logs(ts,user_id,device_id,request_id,action,ok,reason,created_at) VALUES(?,?,?,?,?,?,?,?)",
        (int(time.time()), user_id, device_id, request_id, action, 1 if ok else 0, reason, int(time.time()))
    )
    con.commit()
    con.close()

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if API_KEY:
        key = request.headers.get("x-api-key")
        if key != API_KEY:
            audit("api_key_check", False, "invalid_api_key")
            return HTMLResponse("Unauthorized", status_code=401)
    return await call_next(request)

@app.post("/v1/identity-events")
def post_identity_event(evt: IdentityEvent):
    now = int(time.time())
    # time skew check
    if abs(evt.ts - now) > ALLOWED_SKEW_SECONDS:
        audit("post_identity_event", False, "ts_skew", evt.user_id, evt.device_id, evt.request_id)
        raise HTTPException(status_code=400, detail="timestamp_out_of_range")

    con = db()
    try:
        con.execute("""
            INSERT INTO identity_events(ts,user_id,device_id,request_id,tier_used,index_value,slope,dynamic_id,risk,coercion,signature,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """, (evt.ts, evt.user_id, evt.device_id, evt.request_id, evt.tier_used, float(evt.index), float(evt.slope),
              evt.dynamic_id, int(evt.risk), 1 if evt.coercion else 0, evt.signature, now))
        con.commit()
    except sqlite3.IntegrityError:
        con.close()
        audit("post_identity_event", False, "replay_request_id", evt.user_id, evt.device_id, evt.request_id)
        raise HTTPException(status_code=200, detail="replay_request_id")
    con.close()
    audit("post_identity_event", True, "ok", evt.user_id, evt.device_id, evt.request_id)
    return {"ok": True}

@app.post("/v1/verify")
def verify(req: VerifyRequest):
    con = db()
    row = con.execute("""
        SELECT dynamic_id FROM identity_events
        WHERE user_id=? AND device_id=?
        ORDER BY ts DESC
        LIMIT 1
    """, (req.user_id, req.device_id)).fetchone()
    con.close()

    if not row:
        audit("verify", False, "no_events", req.user_id, req.device_id, req.request_id)
        return {"verified": False, "reason": "no_events"}

    expected = row["dynamic_id"]
    if req.dynamic_id != expected:
        audit("verify", False, "mismatch", req.user_id, req.device_id, req.request_id)
        return {"verified": False, "reason": "mismatch"}

    audit("verify", True, "ok", req.user_id, req.device_id, req.request_id)
    return {"verified": True, "reason": "ok"}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    con = db()
    events = con.execute("""
        SELECT ts,user_id,device_id,tier_used,index_value,slope,dynamic_id,risk,coercion,request_id
        FROM identity_events ORDER BY ts DESC LIMIT 200
    """).fetchall()
    audits = con.execute("""
        SELECT ts,action,ok,reason,user_id,device_id,request_id
        FROM audit_logs ORDER BY ts DESC LIMIT 200
    """).fetchall()
    con.close()

    def badge(ok: bool):
        return '<span class="badge ok">OK</span>' if ok else '<span class="badge bad">FAIL</span>'

    rows = []
    for e in events:
        coercion = bool(e["coercion"])
        rows.append(f"""
        <tr>
          <td>{e["ts"]}</td>
          <td>{e["user_id"]}</td>
          <td>{e["device_id"]}</td>
          <td><span class="badge tier">{e["tier_used"]}</span></td>
          <td>{e["index_value"]:.3f}</td>
          <td>{e["slope"]:.3f}</td>
          <td class="mono">{e["dynamic_id"][:18]}…</td>
          <td><span class="badge risk {'high' if e['risk']>=70 else 'mid' if e['risk']>=30 else 'low'}">{e["risk"]}</span></td>
          <td>{'<span class="badge bad">COERCION</span>' if coercion else '<span class="badge ok">OK</span>'}</td>
          <td class="mono">{e["request_id"][:8]}…</td>
        </tr>
        """)

    arows = []
    for a in audits:
        arows.append(f"""
        <tr>
          <td>{a["ts"]}</td>
          <td>{a["action"]}</td>
          <td>{badge(bool(a["ok"]))}</td>
          <td>{a["reason"] or ""}</td>
          <td>{a["user_id"] or ""}</td>
          <td>{a["device_id"] or ""}</td>
          <td class="mono">{(a["request_id"] or "")[:8]}…</td>
        </tr>
        """)

    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1"/>
      <title>MitoPulse Enterprise Dashboard</title>
      <style>
        body {{ background:#0b0f14; color:#e6edf3; font-family: ui-sans-serif,system-ui; margin:0; }}
        header {{ padding:18px 22px; border-bottom:1px solid #1f2a37; display:flex; align-items:center; justify-content:space-between; }}
        h1 {{ font-size:18px; margin:0; letter-spacing:0.4px; }}
        .wrap {{ padding:18px 22px; }}
        .grid {{ display:grid; grid-template-columns: 1fr; gap:16px; }}
        @media (min-width: 1100px) {{ .grid {{ grid-template-columns: 2fr 1fr; }} }}
        .card {{ background:#0f1620; border:1px solid #1f2a37; border-radius:14px; padding:14px; box-shadow: 0 10px 25px rgba(0,0,0,0.25); }}
        table {{ width:100%; border-collapse: collapse; font-size:12px; }}
        th,td {{ border-bottom: 1px solid #1f2a37; padding:10px 8px; text-align:left; vertical-align:top; }}
        th {{ color:#9fb0c3; font-weight:600; }}
        .badge {{ display:inline-block; padding:3px 8px; border-radius:999px; font-size:11px; border:1px solid #223042; }}
        .badge.ok {{ background:#0b2a16; color:#b7f7c6; border-color:#1e5131; }}
        .badge.bad {{ background:#2a0b0b; color:#ffb0b0; border-color:#6a1f1f; }}
        .badge.tier {{ background:#0b1d2a; color:#a9d7ff; border-color:#1f476a; }}
        .badge.risk.low {{ background:#0b2a16; color:#b7f7c6; border-color:#1e5131; }}
        .badge.risk.mid {{ background:#2a220b; color:#ffe7a8; border-color:#6a5a1f; }}
        .badge.risk.high {{ background:#2a0b0b; color:#ffb0b0; border-color:#6a1f1f; }}
        .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
        .muted {{ color:#9fb0c3; font-size:12px; }}
      </style>
    </head>
    <body>
      <header>
        <div>
          <h1>MitoPulse Enterprise Dashboard</h1>
          <div class="muted">Local-first identity events • anti-replay • audit logs</div>
        </div>
        <div class="muted">DB: {DB_PATH}</div>
      </header>
      <div class="wrap">
        <div class="grid">
          <div class="card">
            <h2 style="margin:0 0 10px 0; font-size:14px;">Identity Events (últimos 200)</h2>
            <table>
              <thead>
                <tr>
                  <th>ts</th><th>user</th><th>device</th><th>tier</th><th>index</th><th>slope</th><th>dynamic_id</th><th>risk</th><th>coercion</th><th>request</th>
                </tr>
              </thead>
              <tbody>
                {''.join(rows) if rows else '<tr><td colspan="10" class="muted">No hay eventos aún.</td></tr>'}
              </tbody>
            </table>
          </div>
          <div class="card">
            <h2 style="margin:0 0 10px 0; font-size:14px;">Audit Logs (últimos 200)</h2>
            <table>
              <thead>
                <tr><th>ts</th><th>action</th><th>ok</th><th>reason</th><th>user</th><th>device</th><th>req</th></tr>
              </thead>
              <tbody>
                {''.join(arows) if arows else '<tr><td colspan="7" class="muted">No hay auditoría aún.</td></tr>'}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(html)
