from __future__ import annotations

import os
import sqlite3
import time
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="MitoPulse MVP Backend", version="0.2.0")

DB = os.environ.get("MITOPULSE_DB", "./mitopulse.db")
ALLOWED_SKEW_SECONDS = int(os.environ.get("MITOPULSE_ALLOWED_SKEW_SECONDS", "600"))  # 10 minutes


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = db()
    cur = conn.cursor()

    # Only derived values are stored (never raw physiological signals)
    cur.execute(
        """CREATE TABLE IF NOT EXISTS identity_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            user_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            ts INTEGER NOT NULL,
            dynamic_id TEXT NOT NULL,
            mitopulse_index REAL NOT NULL,
            slope REAL NOT NULL
        )"""
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_user_device_ts ON identity_events(user_id, device_id, ts DESC)")

    # Verification attempts for anti-replay
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


class IdentityEvent(BaseModel):
    """Derived identity event computed locally (Local-First)."""

    event_id: str = Field(..., description="Client-generated UUID for idempotency")
    user_id: str
    device_id: str
    ts: int = Field(..., description="Unix timestamp (seconds)")
    dynamic_id: str
    mitopulse_index: float
    slope: float


class VerifyRequest(BaseModel):
    """On-demand verification request (anti-replay enforced via request_id)."""

    request_id: str = Field(..., description="Client-generated UUID (one-time)")
    user_id: str
    device_id: str
    ts: int = Field(..., description="Unix timestamp (seconds)")
    dynamic_id: str


def _now() -> int:
    return int(time.time())


@app.post("/v1/identity-events")
def post_event(evt: IdentityEvent) -> Dict[str, Any]:
    """Stores a derived identity event. Idempotent on event_id."""
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO identity_events(event_id, user_id, device_id, ts, dynamic_id, mitopulse_index, slope)
               VALUES (?,?,?,?,?,?,?)""",
            (evt.event_id, evt.user_id, evt.device_id, evt.ts, evt.dynamic_id, evt.mitopulse_index, evt.slope),
        )
        conn.commit()
        return {"status": "ok"}
    except sqlite3.IntegrityError:
        # Duplicate event_id -> treat as success
        return {"status": "ok", "idempotent": True}
    finally:
        conn.close()


@app.post("/v1/verify")
def verify(req: VerifyRequest) -> Dict[str, Any]:
    """Verifies a dynamic_id by matching against the latest known event and enforcing anti-replay."""
    now = _now()

    if abs(now - req.ts) > ALLOWED_SKEW_SECONDS:
        verified, reason = False, "time_skew"
    else:
        conn = db()
        cur = conn.cursor()
        try:
            # Anti-replay: request_id can only be used once
            cur.execute("SELECT 1 FROM verify_attempts WHERE request_id=?", (req.request_id,))
            if cur.fetchone():
                verified, reason = False, "replay_request_id"
            else:
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

            # Persist attempt
            try:
                cur.execute(
                    """INSERT INTO verify_attempts(request_id, user_id, device_id, ts, dynamic_id, verified, reason, created_at)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        req.request_id,
                        req.user_id,
                        req.device_id,
                        req.ts,
                        req.dynamic_id,
                        1 if verified else 0,
                        reason,
                        now,
                    ),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # If it's a replay and already in DB, just return the failure
                pass
        finally:
            conn.close()

    return {"verified": bool(verified), "reason": reason}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    """Simple dashboard (no frontend build needed)."""
    conn = db()
    cur = conn.cursor()

    cur.execute(
        """SELECT user_id, device_id, ts, substr(dynamic_id,1,12) AS dyn, mitopulse_index, slope
           FROM identity_events ORDER BY ts DESC LIMIT 50"""
    )
    events = cur.fetchall()

    cur.execute(
        """SELECT user_id, device_id, ts, substr(dynamic_id,1,12) AS dyn, verified, reason, created_at
           FROM verify_attempts ORDER BY created_at DESC LIMIT 50"""
    )
    verifs = cur.fetchall()

    conn.close()

    def render_rows(rows: List[sqlite3.Row], cols: List[str]) -> str:
        return "\n".join(
            "<tr>" + "".join(f"<td>{r[c]}</td>" for c in cols) + "</tr>" for r in rows
        )

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>MitoPulse MVP Dashboard</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }}
    h1 {{ margin: 0 0 6px 0; }}
    .muted {{ color: #555; margin-bottom: 18px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 10px 0 24px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 14px; }}
    th {{ background: #f6f6f6; text-align: left; }}
    code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>MitoPulse MVP Dashboard</h1>
  <div class=\"muted\">DB: <code>{DB}</code> | Allowed time skew: <code>{ALLOWED_SKEW_SECONDS}s</code> | Docs: <a href=\"/docs\">/docs</a></div>

  <h2>Latest identity events (derived only)</h2>
  <table>
    <thead><tr><th>User</th><th>Device</th><th>ts</th><th>dynamic_id</th><th>index</th><th>slope</th></tr></thead>
    <tbody>
      {render_rows(events, ["user_id","device_id","ts","dyn","mitopulse_index","slope"])}
    </tbody>
  </table>

  <h2>Latest verifications</h2>
  <table>
    <thead><tr><th>User</th><th>Device</th><th>ts</th><th>dynamic_id</th><th>verified</th><th>reason</th><th>created_at</th></tr></thead>
    <tbody>
      {render_rows(verifs, ["user_id","device_id","ts","dyn","verified","reason","created_at"])}
    </tbody>
  </table>
</body>
</html>"""
