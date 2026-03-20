import time, hmac, hashlib
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from jinja2 import Environment, FileSystemLoader, select_autoescape

API_KEY = "demo-key"
ALLOWED_SKEW_SECONDS = 24 * 3600
RATE_LIMIT_PER_MIN = 120

REQUEST_IDS: set[str] = set()
AUDIT: List[Dict[str, Any]] = []
EVENTS: List[Dict[str, Any]] = []
STATE: Dict[str, Dict[str, Any]] = {}
RL: Dict[str, Any] = {}

app = FastAPI(title="MitoPulse One API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
jinja = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(["html","xml"]))

class Signals(BaseModel):
    hr: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    spo2: Optional[float] = None
    sleep_score: Optional[float] = None
    load: Optional[float] = None

class Env(BaseModel):
    altitude_m: Optional[float] = 0
    temp_c: Optional[float] = 22
    humidity_pct: Optional[float] = 50
    pressure_hpa: Optional[float] = 1013

class IdentityEventIn(BaseModel):
    ts: int = Field(..., description="Unix epoch seconds")
    user_id: str
    device_id: str
    request_id: str
    tier: str
    index: float
    slope: float = 0.0
    risk: int = 0
    coercion: bool = False
    stability: float = 1.0
    human_conf: float = 0.9
    dynamic_id: str
    signature: str = Field(..., description="HMAC-SHA256(api_key, user|device|ts|dynamic_id) hex")
    signals: Optional[Signals] = None
    env: Optional[Env] = None

class VerifyIn(BaseModel):
    ts: int
    user_id: str
    device_id: str
    request_id: str
    dynamic_id: str
    signature: str

class VerifyOut(BaseModel):
    verified: bool
    reason: str

def now() -> int:
    return int(time.time())

def audit(action: str, result: str, meta: str = ""):
    AUDIT.insert(0, {"ts": now(), "action": action, "result": result, "meta": meta})
    del AUDIT[2000:]

def check_rate_limit(ip: str):
    t = now()
    w = RL.get(ip)
    if not w or t - w["start"] >= 60:
        RL[ip] = {"start": t, "count": 1}
        return
    w["count"] += 1
    if w["count"] > RATE_LIMIT_PER_MIN:
        raise HTTPException(status_code=429, detail="rate_limited")

def require_api_key(x_api_key: Optional[str]):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="unauthorized")

def sign_payload(secret: bytes, user_id: str, device_id: str, ts: int, dynamic_id: str) -> str:
    msg = f"{user_id}|{device_id}|{ts}|{dynamic_id}".encode("utf-8")
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()

def update_baseline(key: str, index: float, signals: Optional[Signals]):
    st = STATE.get(key) or {"history": []}
    hist = st["history"]
    hist.append(index)
    hist = hist[-30:]
    st["history"] = hist
    mean = sum(hist) / len(hist)
    var = sum((x - mean) ** 2 for x in hist) / max(1, len(hist))
    std = var ** 0.5
    st["mean"] = mean
    st["std"] = std
    st["last_index"] = index
    st["last_seen"] = now()
    if signals:
        st["last_signals"] = signals.model_dump()
    STATE[key] = st
    return mean, std

def compute_stability(index: float, mean: float, std: float) -> float:
    if std <= 1e-6:
        return 1.0
    z = abs(index - mean) / (std + 1e-6)
    return float(max(0.0, min(1.0, 1.0 / (1.0 + (z ** 2)))))

def compute_human_conf(signals: Optional[Signals]) -> float:
    if not signals:
        return 0.75
    score = 0.85
    if signals.hr is not None and (signals.hr < 35 or signals.hr > 210): score -= 0.25
    if signals.spo2 is not None and (signals.spo2 < 80 or signals.spo2 > 100): score -= 0.15
    if signals.hrv_rmssd is not None and (signals.hrv_rmssd < 5 or signals.hrv_rmssd > 250): score -= 0.15
    return float(max(0.0, min(0.99, score)))

@app.get("/health")
def health():
    return {"ok": True, "ts": now(), "version": app.version}

@app.post("/identity/event")
def post_identity_event(ev: IdentityEventIn, request: Request, x_api_key: Optional[str] = Header(default=None)):
    ip = request.client.host if request.client else "unknown"
    check_rate_limit(ip); require_api_key(x_api_key)

    if abs(now() - ev.ts) > ALLOWED_SKEW_SECONDS:
        audit("identity_event", "skew_rejected", f"ip={ip} user={ev.user_id} device={ev.device_id}")
        raise HTTPException(status_code=400, detail="timestamp_out_of_range")

    if ev.request_id in REQUEST_IDS:
        audit("identity_event", "replay_request_id", f"ip={ip} user={ev.user_id} device={ev.device_id}")
        raise HTTPException(status_code=409, detail="replay_request_id")
    REQUEST_IDS.add(ev.request_id)

    expected = sign_payload(API_KEY.encode("utf-8"), ev.user_id, ev.device_id, ev.ts, ev.dynamic_id)
    if not hmac.compare_digest(expected, ev.signature):
        audit("identity_event", "bad_signature", f"ip={ip} user={ev.user_id} device={ev.device_id}")
        raise HTTPException(status_code=400, detail="bad_signature")

    key = f"{ev.user_id}|{ev.device_id}"
    mean, std = update_baseline(key, ev.index, ev.signals)
    stability = compute_stability(ev.index, mean, std)
    human_conf = compute_human_conf(ev.signals)
    coercion = ev.coercion or (ev.risk >= 60) or (stability < 0.25 and ev.risk >= 40)

    rec = ev.model_dump()
    rec["stability"] = stability
    rec["human_conf"] = human_conf
    rec["coercion"] = coercion
    EVENTS.insert(0, rec); del EVENTS[2000:]

    STATE[key].update({"tier": ev.tier, "risk": ev.risk, "coercion": coercion, "stability": stability,
                       "human_conf": human_conf, "dynamic_id": ev.dynamic_id, "ts": ev.ts})

    audit("identity_event", "ok", f"ip={ip} user={ev.user_id} device={ev.device_id}")
    return {"ok": True, "stability": stability, "human_conf": human_conf, "coercion": coercion}

@app.post("/identity/verify", response_model=VerifyOut)
def verify(v: VerifyIn, request: Request, x_api_key: Optional[str] = Header(default=None)):
    ip = request.client.host if request.client else "unknown"
    check_rate_limit(ip); require_api_key(x_api_key)

    if v.request_id in REQUEST_IDS:
        audit("verify", "replay_request_id", f"ip={ip} user={v.user_id} device={v.device_id}")
        return VerifyOut(verified=False, reason="replay_request_id")
    REQUEST_IDS.add(v.request_id)

    expected = sign_payload(API_KEY.encode("utf-8"), v.user_id, v.device_id, v.ts, v.dynamic_id)
    if not hmac.compare_digest(expected, v.signature):
        audit("verify", "bad_signature", f"ip={ip} user={v.user_id} device={v.device_id}")
        return VerifyOut(verified=False, reason="bad_signature")

    key = f"{v.user_id}|{v.device_id}"
    st = STATE.get(key)
    if not st:
        audit("verify", "unknown_user", f"ip={ip} user={v.user_id} device={v.device_id}")
        return VerifyOut(verified=False, reason="unknown_user")

    if st.get("dynamic_id") != v.dynamic_id:
        audit("verify", "mismatch", f"ip={ip} user={v.user_id} device={v.device_id}")
        return VerifyOut(verified=False, reason="mismatch")

    audit("verify", "ok", f"ip={ip} user={v.user_id} device={v.device_id}")
    return VerifyOut(verified=True, reason="ok")

@app.get("/identity/state")
def identity_state(user_id: str, device_id: str, request: Request, x_api_key: Optional[str] = Header(default=None)):
    ip = request.client.host if request.client else "unknown"
    check_rate_limit(ip); require_api_key(x_api_key)
    key = f"{user_id}|{device_id}"
    st = STATE.get(key)
    if not st:
        raise HTTPException(status_code=404, detail="unknown_user")
    return {"user_id": user_id, "device_id": device_id, "tier": st.get("tier"),
            "risk": st.get("risk"), "coercion": st.get("coercion"), "stability": st.get("stability"),
            "human_conf": st.get("human_conf"), "baseline_mean": st.get("mean"), "baseline_std": st.get("std"),
            "dynamic_id": st.get("dynamic_id"), "ts": st.get("ts")}

@app.get("/identity/human-proof")
def human_proof(user_id: str, device_id: str, request: Request, x_api_key: Optional[str] = Header(default=None)):
    ip = request.client.host if request.client else "unknown"
    check_rate_limit(ip); require_api_key(x_api_key)
    key = f"{user_id}|{device_id}"
    st = STATE.get(key)
    if not st:
        raise HTTPException(status_code=404, detail="unknown_user")
    return {"human_conf": st.get("human_conf", 0.0), "ts": now(), "ok": True}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    tmpl = jinja.get_template("dashboard.html")
    stats = {"events": len(EVENTS),
             "verifies": sum(1 for a in AUDIT if a["action"] == "verify"),
             "coercions": sum(1 for e in EVENTS if e.get("coercion")),
             "replays": sum(1 for a in AUDIT if a["result"] == "replay_request_id")}
    html = tmpl.render(stats=stats, events=EVENTS[:50], audits=AUDIT[:60])
    return HTMLResponse(html)

