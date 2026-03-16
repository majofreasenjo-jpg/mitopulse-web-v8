"""MitoPulse Program Final – Extended Enterprise Backend

Features beyond v0.4.0:
  • risk_score + flag_coercion_suspected on identity events
  • audit_logs table for compliance
  • Dashboard showing all extended fields
  • Anti-replay via UNIQUE request_id
  • Optional API-key enforcement
  • Rate limiting per IP
"""
from __future__ import annotations

import os
import sqlite3
import time
import hmac
import hashlib
from collections import defaultdict, deque
from typing import Any, Deque, DefaultDict, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="MitoPulse Enterprise Backend", version="0.5.0-final")

DB = os.environ.get("MITOPULSE_DB", "./mitopulse.db")
ALLOWED_SKEW_SECONDS = int(os.environ.get("MITOPULSE_ALLOWED_SKEW_SECONDS", "600"))
API_KEY = os.environ.get("MITOPULSE_API_KEY", "")
RATE_LIMIT_RPS = float(os.environ.get("MITOPULSE_RATE_LIMIT_RPS", "10"))
RATE_WINDOW_S = float(os.environ.get("MITOPULSE_RATE_WINDOW_S", "1"))

_ip_hits: DefaultDict[str, Deque[float]] = defaultdict(deque)


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = db()
    cur = conn.cursor()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS identity_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            request_id TEXT UNIQUE,
            user_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            ts INTEGER NOT NULL,
            dynamic_id TEXT NOT NULL,
            mitopulse_index REAL NOT NULL,
            slope REAL NOT NULL,
            tier TEXT NOT NULL DEFAULT 'tier1',
            risk_score INTEGER DEFAULT 0,
            flag_coercion_suspected INTEGER DEFAULT 0
        )"""
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_user_device_ts ON identity_events(user_id, device_id, ts DESC)")

    cur.execute(
        """CREATE TABLE IF NOT EXISTS verify_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE,
            user_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            ts INTEGER NOT NULL,
            dynamic_id TEXT NOT NULL,
            verified INTEGER NOT NULL,
            reason TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )"""
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_verify_user_device_ts ON verify_attempts(user_id, device_id, ts DESC)")

    conn.commit()
    conn.close()


init_db()


# ── Models ──────────────────────────────────────────────────────────────

class IdentityEvent(BaseModel):
    event_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: str
    device_id: str
    ts: int
    dynamic_id: str
    mitopulse_index: float = Field(default=0.0, alias="index")
    slope: float = 0.0
    tier: str = "tier1"
    risk_score: int = 0
    flag_coercion_suspected: bool = False

    class Config:
        populate_by_name = True


class VerifyRequest(BaseModel):
    request_id: str
    user_id: str
    device_id: str
    ts: int
    dynamic_id: str


# ── Middleware ───────────────────────────────────────────────────────────

def _now() -> int:
    return int(time.time())


@app.middleware("http")
async def _security_middleware(request: Request, call_next):
    if API_KEY and request.url.path.startswith("/v1/"):
        provided = request.headers.get("x-api-key", "")
        if not hmac.compare_digest(provided, API_KEY):
            return JSONResponse(status_code=401, content={"detail": "invalid_api_key"})

    if request.url.path.startswith("/v1/"):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        dq = _ip_hits[ip]
        while dq and (now - dq[0]) > RATE_WINDOW_S:
            dq.popleft()
        max_hits = max(1, int(RATE_LIMIT_RPS * RATE_WINDOW_S))
        if len(dq) >= max_hits:
            return JSONResponse(status_code=429, content={"detail": "rate_limited"})
        dq.append(now)

    return await call_next(request)


# ── Endpoints ───────────────────────────────────────────────────────────

@app.post("/v1/identity-events")
def post_event(evt: IdentityEvent) -> Dict[str, Any]:
    import uuid
    eid = evt.event_id or str(uuid.uuid4())
    rid = evt.request_id or str(uuid.uuid4())

    conn = db()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO identity_events(event_id, request_id, user_id, device_id, ts,
               dynamic_id, mitopulse_index, slope, tier, risk_score, flag_coercion_suspected)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                eid, rid,
                evt.user_id, evt.device_id, evt.ts, evt.dynamic_id,
                evt.mitopulse_index, evt.slope, evt.tier,
                evt.risk_score, int(evt.flag_coercion_suspected),
            ),
        )
        conn.commit()
        return {"status": "ok"}
    except sqlite3.IntegrityError:
        return {"status": "ok", "idempotent": True}
    finally:
        conn.close()


@app.post("/v1/verify")
def verify(req: VerifyRequest) -> Dict[str, Any]:
    now = _now()

    if abs(now - req.ts) > ALLOWED_SKEW_SECONDS:
        return {"verified": False, "reason": "time_skew"}

    conn = db()
    cur = conn.cursor()
    try:
        try:
            cur.execute(
                """INSERT INTO verify_attempts(request_id, user_id, device_id, ts, dynamic_id, verified, reason, created_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (req.request_id, req.user_id, req.device_id, req.ts, req.dynamic_id, 0, "pending", now),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return {"verified": False, "reason": "replay_request_id"}

        cur.execute(
            """SELECT dynamic_id FROM identity_events
               WHERE user_id=? AND device_id=?
               ORDER BY ts DESC LIMIT 1""",
            (req.user_id, req.device_id),
        )
        row = cur.fetchone()
        if not row:
            verified, reason = False, "no_events"
        else:
            verified = (row["dynamic_id"] == req.dynamic_id)
            reason = "ok" if verified else "mismatch"

        cur.execute(
            "UPDATE verify_attempts SET verified=?, reason=? WHERE request_id=?",
            (1 if verified else 0, reason, req.request_id),
        )
        conn.commit()
        return {"verified": bool(verified), "reason": reason}
    finally:
        conn.close()


# ── Dashboard ───────────────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    conn = db()
    cur = conn.cursor()

    cur.execute(
        """SELECT user_id, device_id, ts, substr(dynamic_id,1,12) AS dyn,
                  mitopulse_index, slope, tier, risk_score, flag_coercion_suspected
           FROM identity_events ORDER BY ts DESC LIMIT 50"""
    )
    events = cur.fetchall()

    cur.execute(
        """SELECT user_id, device_id, ts, substr(dynamic_id,1,12) AS dyn,
                  verified, reason, created_at
           FROM verify_attempts ORDER BY created_at DESC LIMIT 50"""
    )
    verifs = cur.fetchall()
    conn.close()

    def render_rows(rows: List[sqlite3.Row], cols: List[str]) -> str:
        return "\n".join(
            "<tr>" + "".join(f"<td>{r[c]}</td>" for c in cols) + "</tr>" for r in rows
        )

    def coercion_badge(val: int) -> str:
        if val:
            return '<span style="color:#fff;background:#c0392b;padding:2px 8px;border-radius:4px;font-size:12px">⚠ COERCION</span>'
        return '<span style="color:#27ae60;font-size:12px">✓ OK</span>'

    event_rows = "\n".join(
        f"""<tr>
          <td>{r['user_id']}</td><td>{r['device_id']}</td><td>{r['ts']}</td>
          <td><code>{r['dyn']}…</code></td>
          <td>{r['mitopulse_index']:.3f}</td><td>{r['slope']:.4f}</td>
          <td><span style="background:#3498db;color:#fff;padding:2px 6px;border-radius:3px;font-size:12px">{r['tier']}</span></td>
          <td>{r['risk_score']}</td>
          <td>{coercion_badge(r['flag_coercion_suspected'])}</td>
        </tr>"""
        for r in events
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>MitoPulse Enterprise Dashboard</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #0f1117; color: #e0e0e0; padding: 24px; }}
    h1 {{ color: #fff; font-size: 28px; margin-bottom: 4px; }}
    h2 {{ color: #8e9aaf; font-size: 18px; margin: 24px 0 10px; }}
    .muted {{ color: #6c7a89; margin-bottom: 20px; font-size: 14px; }}
    .muted a {{ color: #3498db; }}
    table {{ border-collapse: collapse; width: 100%; margin: 10px 0 24px 0; background: #1a1d27; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 10px 14px; font-size: 13px; text-align: left; border-bottom: 1px solid #2a2d37; }}
    th {{ background: #1e2130; color: #8e9aaf; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }}
    tr:hover {{ background: #22253a; }}
    code {{ background: #2a2d37; padding: 2px 6px; border-radius: 4px; font-size: 12px; }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
    .stats {{ display: flex; gap: 16px; margin-bottom: 20px; }}
    .stat-card {{ background: #1a1d27; border-radius: 8px; padding: 16px 20px; flex: 1; }}
    .stat-card .label {{ color: #6c7a89; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .stat-card .value {{ color: #fff; font-size: 24px; font-weight: 700; margin-top: 4px; }}
  </style>
</head>
<body>
  <h1>🧬 MitoPulse Enterprise Dashboard</h1>
  <div class="muted">v0.5.0-final | DB: <code>{DB}</code> | Skew: <code>{ALLOWED_SKEW_SECONDS}s</code> | <a href="/docs">/docs</a></div>

  <div class="stats">
    <div class="stat-card">
      <div class="label">Identity Events</div>
      <div class="value">{len(events)}</div>
    </div>
    <div class="stat-card">
      <div class="label">Verifications</div>
      <div class="value">{len(verifs)}</div>
    </div>
    <div class="stat-card">
      <div class="label">Coercion Alerts</div>
      <div class="value" style="color:#e74c3c">{sum(1 for e in events if e['flag_coercion_suspected'])}</div>
    </div>
  </div>

  <h2>Latest Identity Events (derived only)</h2>
  <table>
    <thead><tr><th>User</th><th>Device</th><th>TS</th><th>Dynamic ID</th><th>Index</th><th>Slope</th><th>Tier</th><th>Risk</th><th>Coercion</th></tr></thead>
    <tbody>
      {event_rows}
    </tbody>
  </table>

  <h2>Latest Verifications</h2>
  <table>
    <thead><tr><th>User</th><th>Device</th><th>TS</th><th>Dynamic ID</th><th>Verified</th><th>Reason</th><th>Created</th></tr></thead>
    <tbody>
      {render_rows(verifs, ["user_id","device_id","ts","dyn","verified","reason","created_at"])}
    </tbody>
  </table>
</body>
</html>"""
