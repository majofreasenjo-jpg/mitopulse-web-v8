
from __future__ import annotations
import os, json, hmac, hashlib, sqlite3
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from jinja2 import Environment, FileSystemLoader, select_autoescape

DB_PATH = os.environ.get("MITOPULSE_DB", os.path.join(os.path.dirname(__file__), "mitopulse.db"))
API_KEY = os.environ.get("MITOPULSE_API_KEY", "")
ALLOWED_SKEW_SECONDS = int(os.environ.get("MITOPULSE_ALLOWED_SKEW_SECONDS", "86400"))

app = FastAPI(title="MitoPulse v2.5 Backend", version="0.2.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja = Environment(loader=FileSystemLoader(templates_dir), autoescape=select_autoescape(["html","xml"]))

def db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS identity_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        device_id TEXT NOT NULL,
        ts INTEGER NOT NULL,
        request_id TEXT NOT NULL UNIQUE,
        tier TEXT,
        index_value REAL,
        slope REAL,
        risk INTEGER,
        coercion INTEGER,
        dynamic_id TEXT,
        signature TEXT,
        human_confidence REAL,
        hr REAL, hrv_rmssd REAL, spo2 REAL, sleep_score REAL, load REAL,
        altitude_m REAL, temp_c REAL, humidity_pct REAL, pressure_hpa REAL,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER NOT NULL,
        action TEXT NOT NULL,
        user_id TEXT,
        device_id TEXT,
        request_id TEXT,
        status TEXT NOT NULL,
        reason TEXT,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS baselines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        device_id TEXT NOT NULL,
        baseline_index REAL NOT NULL,
        baseline_std REAL NOT NULL,
        window_days INTEGER NOT NULL,
        updated_ts INTEGER NOT NULL,
        UNIQUE(user_id, device_id)
    )
    """)
    con.commit()
    con.close()

init_db()

def audit(action: str, ts: int, status: str, reason: str="", user_id: str="", device_id: str="", request_id: str=""):
    con = db()
    con.execute(
        "INSERT INTO audit_logs (ts, action, user_id, device_id, request_id, status, reason, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (ts, action, user_id, device_id, request_id, status, reason, now_iso()),
    )
    con.commit()
    con.close()

def require_api_key(req: Request):
    if not API_KEY:
        return
    if req.headers.get("X-API-Key","") != API_KEY:
        raise HTTPException(status_code=401, detail="invalid_api_key")

def clamp(x: float, lo: float=0.0, hi: float=1.0) -> float:
    return max(lo, min(hi, x))

def stability_score(idx: float, baseline_idx: float, baseline_std: float) -> float:
    import math
    sigma = max(baseline_std, 0.05)
    z = abs(idx - baseline_idx) / sigma
    return clamp(math.exp(-z))

def compute_baseline(user_id: str, device_id: str, window_days: int=30) -> Tuple[float,float,int]:
    con = db()
    cur = con.cursor()
    cur.execute("SELECT index_value FROM identity_events WHERE user_id=? AND device_id=? ORDER BY ts DESC LIMIT 200", (user_id, device_id))
    vals = [r[0] for r in cur.fetchall() if r[0] is not None]
    con.close()
    if len(vals) < 3:
        return (0.6, 0.08, window_days)
    import statistics
    mean = statistics.mean(vals)
    std = statistics.pstdev(vals) if len(vals) >= 2 else 0.08
    return (float(mean), float(max(std, 0.02)), window_days)

def upsert_baseline(user_id: str, device_id: str, baseline_idx: float, baseline_std: float, window_days: int, updated_ts: int):
    con = db()
    con.execute("""
    INSERT INTO baselines (user_id, device_id, baseline_index, baseline_std, window_days, updated_ts)
    VALUES (?,?,?,?,?,?)
    ON CONFLICT(user_id, device_id) DO UPDATE SET
      baseline_index=excluded.baseline_index,
      baseline_std=excluded.baseline_std,
      window_days=excluded.window_days,
      updated_ts=excluded.updated_ts
    """, (user_id, device_id, baseline_idx, baseline_std, window_days, updated_ts))
    con.commit()
    con.close()

def get_baseline(user_id: str, device_id: str) -> Optional[Dict[str,Any]]:
    con = db()
    row = con.execute("SELECT * FROM baselines WHERE user_id=? AND device_id=?", (user_id, device_id)).fetchone()
    con.close()
    return dict(row) if row else None

def canonical_json(payload: Dict[str,Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",",":")).encode("utf-8")

def verify_signature_if_present(payload: Dict[str,Any]) -> Tuple[bool,str]:
    require_sig = os.environ.get("MITOPULSE_REQUIRE_SIG","0") == "1"
    sig = payload.get("signature")
    if not sig:
        return ((not require_sig), "missing_signature" if require_sig else "ok")

    demo_secret = os.environ.get("MITOPULSE_DEMO_DEVICE_SECRET","").encode("utf-8")
    if not demo_secret:
        return (True, "ok")

    copy = dict(payload)
    copy.pop("signature", None)
    exp = hmac.new(demo_secret, canonical_json(copy), hashlib.sha256).digest()
    import base64
    exp_b64 = base64.urlsafe_b64encode(exp).decode("utf-8").rstrip("=")
    return (exp_b64 == sig, "ok" if exp_b64 == sig else "bad_signature")

class IdentityEvent(BaseModel):
    user_id: str
    device_id: str
    ts: int
    request_id: str

    tier: Optional[str] = None
    index: Optional[float] = Field(default=None, alias="index_value")
    slope: Optional[float] = 0.0
    risk: Optional[int] = 0
    coercion: Optional[bool] = False
    dynamic_id: Optional[str] = None
    signature: Optional[str] = None
    human_confidence: Optional[float] = None

    hr: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    spo2: Optional[float] = None
    sleep_score: Optional[float] = None
    load: Optional[float] = None

    altitude_m: Optional[float] = None
    temp_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    pressure_hpa: Optional[float] = None

    class Config:
        populate_by_name = True

class VerifyRequest(BaseModel):
    user_id: str
    device_id: str
    dynamic_id: str
    request_id: str

@app.post("/v1/identity-events")
async def post_identity_event(req: Request, ev: IdentityEvent):
    require_api_key(req)

    now_ts = int(datetime.utcnow().timestamp())
    if abs(ev.ts - now_ts) > ALLOWED_SKEW_SECONDS:
        audit("identity_event", ev.ts, "rejected", "time_skew", ev.user_id, ev.device_id, ev.request_id)
        raise HTTPException(status_code=400, detail="time_skew")

    ok, reason = verify_signature_if_present(ev.model_dump(by_alias=True))
    if not ok:
        audit("identity_event", ev.ts, "rejected", reason, ev.user_id, ev.device_id, ev.request_id)
        raise HTTPException(status_code=400, detail=reason)

    try:
        con = db()
        con.execute("""
            INSERT INTO identity_events (
              user_id, device_id, ts, request_id, tier, index_value, slope, risk, coercion, dynamic_id, signature, human_confidence,
              hr, hrv_rmssd, spo2, sleep_score, load, altitude_m, temp_c, humidity_pct, pressure_hpa, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            ev.user_id, ev.device_id, ev.ts, ev.request_id, ev.tier,
            ev.index, ev.slope, ev.risk, 1 if ev.coercion else 0,
            ev.dynamic_id, ev.signature, ev.human_confidence,
            ev.hr, ev.hrv_rmssd, ev.spo2, ev.sleep_score, ev.load,
            ev.altitude_m, ev.temp_c, ev.humidity_pct, ev.pressure_hpa,
            now_iso()
        ))
        con.commit()
        con.close()
    except sqlite3.IntegrityError:
        audit("identity_event", ev.ts, "rejected", "replay_request_id", ev.user_id, ev.device_id, ev.request_id)
        return JSONResponse({"ok": False, "reason": "replay_request_id"}, status_code=200)

    b_idx, b_std, w = compute_baseline(ev.user_id, ev.device_id, 30)
    upsert_baseline(ev.user_id, ev.device_id, b_idx, b_std, w, ev.ts)

    audit("identity_event", ev.ts, "accepted", "ok", ev.user_id, ev.device_id, ev.request_id)
    return {"ok": True, "reason": "ok"}

@app.post("/v1/verify")
async def verify(req: Request, body: VerifyRequest):
    require_api_key(req)
    now_ts = int(datetime.utcnow().timestamp())

    con = db()
    prev = con.execute("SELECT 1 FROM audit_logs WHERE request_id=? LIMIT 1", (body.request_id,)).fetchone()
    con.close()
    if prev:
        audit("verify", now_ts, "rejected", "replay_request_id", body.user_id, body.device_id, body.request_id)
        return {"verified": False, "reason": "replay_request_id"}

    con = db()
    row = con.execute("SELECT dynamic_id FROM identity_events WHERE user_id=? AND device_id=? ORDER BY ts DESC LIMIT 1",
                      (body.user_id, body.device_id)).fetchone()
    con.close()
    if not row:
        audit("verify", now_ts, "rejected", "no_events", body.user_id, body.device_id, body.request_id)
        return {"verified": False, "reason": "no_events"}
    if row["dynamic_id"] != body.dynamic_id:
        audit("verify", now_ts, "rejected", "mismatch", body.user_id, body.device_id, body.request_id)
        return {"verified": False, "reason": "mismatch"}

    audit("verify", now_ts, "accepted", "ok", body.user_id, body.device_id, body.request_id)
    return {"verified": True, "reason": "ok"}

@app.get("/v2/identity/state")
async def state(req: Request, user_id: str, device_id: str):
    require_api_key(req)
    con = db()
    row = con.execute("SELECT * FROM identity_events WHERE user_id=? AND device_id=? ORDER BY ts DESC LIMIT 1",
                      (user_id, device_id)).fetchone()
    con.close()
    if not row:
        raise HTTPException(status_code=404, detail="no_events")

    base = get_baseline(user_id, device_id)
    if not base:
        b_idx, b_std, w = compute_baseline(user_id, device_id, 30)
        base = {"baseline_index": b_idx, "baseline_std": b_std, "window_days": w, "updated_ts": row["ts"]}

    idx = float(row["index_value"] or 0.0)
    st = stability_score(idx, float(base["baseline_index"]), float(base["baseline_std"]))
    hc = float(row["human_confidence"] or 0.0)

    return {
        "user_id": user_id,
        "device_id": device_id,
        "ts": row["ts"],
        "tier": row["tier"],
        "index": idx,
        "risk": row["risk"],
        "coercion": bool(row["coercion"]),
        "dynamic_id": row["dynamic_id"],
        "baseline": base,
        "stability": st,
        "human_confidence": hc,
    }

@app.get("/v2/identity/human-proof")
async def human_proof(req: Request, user_id: str, device_id: str, threshold: float=0.75):
    require_api_key(req)
    st = await state(req, user_id, device_id)
    conf = float(st["human_confidence"])
    return {"human": conf >= threshold, "confidence": conf, "threshold": threshold}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(req: Request):
    require_api_key(req)
    con = db()
    events = con.execute("""
      SELECT user_id, device_id, ts, tier, index_value, risk, coercion, human_confidence, request_id
      FROM identity_events ORDER BY ts DESC LIMIT 50
    """).fetchall()
    audits = con.execute("""
      SELECT ts, action, status, reason, user_id, device_id, request_id
      FROM audit_logs ORDER BY ts DESC LIMIT 50
    """).fetchall()
    con.close()

    series = [{"ts": r["ts"], "index": r["index_value"] or 0, "risk": r["risk"] or 0} for r in reversed(events[-15:])]
    tpl = jinja.get_template("dashboard.html")
    return tpl.render(events=events, audits=audits, series=json.dumps(series))

@app.get("/")
async def root():
    return {"ok": True, "service": "mitopulse-backend", "version": "v2.5"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT","8000")), reload=True)
