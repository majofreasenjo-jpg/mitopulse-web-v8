from __future__ import annotations
import os, time
from statistics import mean, pstdev
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, select_autoescape

app = FastAPI(title="MitoPulse Product Demo", version="1.0.0")
BASE_DIR = os.path.dirname(__file__)
TEMPLATES = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")), autoescape=select_autoescape(["html"]))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

USERS: Dict[str, Dict[str, Any]] = {}
AUDIT: List[Dict[str, Any]] = []

def log(action: str, payload: dict):
    AUDIT.append({"ts": int(time.time()), "action": action, "payload": payload})
    if len(AUDIT) > 500:
        del AUDIT[0]

class PresenceEvent(BaseModel):
    user_id: str
    device_id: str
    stability: float
    human_conf: float
    risk_signal: int = 0

class VerifyRequest(BaseModel):
    user_id: str
    device_id: str
    stability: float
    human_conf: float
    risk_signal: int = 0

@app.get("/health")
def health():
    return {"status":"ok","product":"MitoPulse Product Demo"}

@app.post("/v1/presence/event")
def presence_event(body: PresenceEvent):
    user = USERS.setdefault(body.user_id, {"user_id": body.user_id, "device_id": body.device_id, "samples": [], "baseline_mean": None, "baseline_std": None, "last_seen": None})
    user["device_id"] = body.device_id
    sample = {"ts": int(time.time()), "stability": body.stability, "human_conf": body.human_conf, "risk_signal": body.risk_signal}
    user["samples"].append(sample)
    user["samples"] = user["samples"][-20:]
    vals = [s["stability"] for s in user["samples"]]
    user["baseline_mean"] = round(mean(vals), 4)
    user["baseline_std"] = round(pstdev(vals), 4) if len(vals) > 1 else 0.0
    user["last_seen"] = int(time.time())
    log("presence_event", {"user_id": body.user_id, "device_id": body.device_id, **sample})
    return {"ok": True, "baseline_mean": user["baseline_mean"], "baseline_std": user["baseline_std"], "samples": len(user["samples"])}

@app.post("/v1/verify/presence")
def verify_presence(body: VerifyRequest):
    user = USERS.get(body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_registered")
    baseline_mean = user["baseline_mean"] if user["baseline_mean"] is not None else body.stability
    baseline_std = user["baseline_std"] if user["baseline_std"] is not None else 0.0
    delta = abs(body.stability - baseline_mean)
    if body.human_conf < 0.55 or body.risk_signal >= 85:
        verdict, reason = "BLOCK", "high_risk_or_low_human_conf"
    elif delta > max(0.25, baseline_std * 3) or body.risk_signal >= 50:
        verdict, reason = "REVIEW", "baseline_deviation_or_medium_risk"
    else:
        verdict, reason = "OK", "stable_baseline"
    res = {"verified": verdict == "OK", "verdict": verdict, "reason": reason, "stability": body.stability, "human_conf": body.human_conf, "baseline_mean": baseline_mean, "baseline_std": baseline_std, "risk_signal": body.risk_signal}
    log("verify_presence", {"user_id": body.user_id, "device_id": body.device_id, **res})
    return res

@app.get("/v1/users")
def users():
    return {"users": [{"user_id": u["user_id"], "device_id": u["device_id"], "baseline_mean": u["baseline_mean"], "baseline_std": u["baseline_std"], "samples": len(u["samples"]), "last_seen": u["last_seen"]} for u in USERS.values()]}

@app.get("/v1/audit")
def audit():
    return {"entries": AUDIT[-200:]}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return TEMPLATES.get_template("dashboard.html").render(users=list(USERS.values()), audit=list(reversed(AUDIT[-200:])))

@app.get("/app", response_class=HTMLResponse)
def app_page():
    return TEMPLATES.get_template("app.html").render()

@app.get("/manifest.webmanifest")
def manifest():
    return FileResponse(os.path.join(BASE_DIR, "static", "manifest.webmanifest"), media_type="application/manifest+json")

@app.get("/service-worker.js")
def sw():
    return FileResponse(os.path.join(BASE_DIR, "static", "service-worker.js"), media_type="application/javascript")
