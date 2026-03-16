
from __future__ import annotations
import base64, json, time, os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from jinja2 import Environment, FileSystemLoader, select_autoescape

app = FastAPI(title="MitoPulse Human Infrastructure v1", version="1.0.0")
devices: Dict[tuple, dict] = {}
states: Dict[tuple, dict] = {}
edges: List[dict] = []
audits: List[dict] = []
replay_seen = set()
recovery_requests: Dict[str, dict] = {}

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(["html"]))

def canonical_json(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")

def log(action: str, status: str, reason: str = "", extra: Optional[dict] = None):
    audits.append({"ts": int(time.time()), "action": action, "status": status, "reason": reason, "extra": extra or {}})
    if len(audits) > 500:
        del audits[0]

def stability_band(stability: float) -> str:
    if stability >= 0.75: return "stable"
    if stability >= 0.45: return "drift"
    return "anomaly"

def add_edge(edge_type: str, src: str, dst: str, weight: float, reason: str):
    edges.append({"ts": int(time.time()), "type": edge_type, "src": src, "dst": dst, "weight": round(weight, 3), "reason": reason})
    if len(edges) > 500:
        del edges[0]

class DeviceRegister(BaseModel):
    tenant_id: str
    user_id: str
    device_id: str
    public_key: str

class PresenceEvent(BaseModel):
    tenant_id: str
    user_id: str
    device_id: str
    ts: int
    request_id: str
    epoch: int
    tier: str
    index: float
    stability: float
    human_conf: float
    risk: int
    coercion: bool
    context: Dict[str, Any] = {}
    signature: str

class ContinuityStart(BaseModel):
    tenant_id: str
    user_id: str
    old_device_id: str
    new_device_id: str

class ContinuityComplete(BaseModel):
    tenant_id: str
    user_id: str
    old_device_id: str
    new_device_id: str
    token: str

class RecoveryRequest(BaseModel):
    tenant_id: str
    user_id: str
    target_device_id: str
    approvers: List[str]

class RecoveryApprove(BaseModel):
    recovery_id: str
    approver_device_id: str

class GroupVerify(BaseModel):
    tenant_id: str
    members: List[dict]
    require_quorum: int = 2
    min_stability: float = 0.55
    max_risk: int = 60

@app.get("/health")
def health():
    return {"status": "ok", "service": "mitopulse-human-infra", "version": "1.0.0"}

@app.post("/v1/devices/register")
def register_device(body: DeviceRegister):
    devices[(body.tenant_id, body.user_id, body.device_id)] = {"public_key": body.public_key, "epoch": 1, "registered_at": int(time.time())}
    log("device_register", "accepted", extra=body.model_dump())
    return {"ok": True, "epoch": 1}

@app.post("/v1/presence/event")
def presence_event(body: PresenceEvent):
    key = (body.tenant_id, body.user_id, body.device_id)
    if key not in devices:
        log("presence_event", "rejected", "unknown_device", {"key": str(key)})
        raise HTTPException(status_code=404, detail="unknown_device")
    if body.request_id in replay_seen:
        log("presence_event", "rejected", "replay_request_id", {"request_id": body.request_id})
        return {"ok": False, "reason": "replay_request_id"}
    packet = body.model_dump()
    sig_b64 = packet.pop("signature")
    try:
        VerifyKey(base64.b64decode(devices[key]["public_key"])).verify(canonical_json(packet), base64.b64decode(sig_b64))
    except BadSignatureError:
        log("presence_event", "rejected", "bad_signature", {"key": str(key)})
        raise HTTPException(status_code=401, detail="bad_signature")

    replay_seen.add(body.request_id)
    band = stability_band(body.stability)
    node_id = f"{body.tenant_id}:{body.user_id}:{body.device_id}:{body.epoch}"
    states[key] = {
        "tenant_id": body.tenant_id, "user_id": body.user_id, "device_id": body.device_id, "epoch": body.epoch,
        "tier": body.tier, "index": body.index, "stability": body.stability, "stability_band": band,
        "human_conf": body.human_conf, "risk": body.risk, "coercion": body.coercion, "context": body.context,
        "node_id": node_id, "last_seen": int(time.time())
    }

    same_tenant = [s for s in states.values() if s["tenant_id"] == body.tenant_id and s["node_id"] != node_id]
    for s in same_tenant:
        if abs(states[key]["last_seen"] - s["last_seen"]) <= 600:
            add_edge("cohab", node_id, s["node_id"], 0.6, "temporal_cooccurrence")
        if body.risk >= 80 and s["risk"] >= 80:
            add_edge("risk", node_id, s["node_id"], 0.8, "shared_high_risk")
    log("presence_event", "accepted", extra={"node_id": node_id, "band": band})
    return {"ok": True, "state": states[key]}

@app.get("/v1/identity/state")
def identity_state(tenant_id: str, user_id: str, device_id: str):
    key = (tenant_id, user_id, device_id)
    if key not in states:
        raise HTTPException(status_code=404, detail="no_state")
    return states[key]

@app.get("/v1/identity/human-proof")
def human_proof(tenant_id: str, user_id: str, device_id: str):
    key = (tenant_id, user_id, device_id)
    if key not in states:
        raise HTTPException(status_code=404, detail="no_state")
    st = states[key]
    return {"human": st["human_conf"] >= 0.8 and st["stability"] >= 0.45 and st["risk"] <= 60, "human_conf": st["human_conf"], "stability": st["stability"], "risk": st["risk"]}

@app.post("/v1/identity/continuity/start")
def continuity_start(body: ContinuityStart):
    old_key = (body.tenant_id, body.user_id, body.old_device_id)
    if old_key not in devices:
        raise HTTPException(status_code=404, detail="old_device_not_found")
    token = base64.b64encode(f"{body.tenant_id}|{body.user_id}|{body.old_device_id}|{body.new_device_id}|{int(time.time())}".encode()).decode()
    log("continuity_start", "accepted", extra=body.model_dump())
    return {"token": token}

@app.post("/v1/identity/continuity/complete")
def continuity_complete(body: ContinuityComplete):
    try:
        tenant_id, user_id, old_device_id, new_device_id, _ = base64.b64decode(body.token).decode().split("|")
    except Exception:
        raise HTTPException(status_code=400, detail="bad_token")
    if (tenant_id, user_id, old_device_id) not in devices or (tenant_id, user_id, new_device_id) not in devices:
        raise HTTPException(status_code=404, detail="device_missing")
    old_epoch = devices[(tenant_id, user_id, old_device_id)]["epoch"]
    devices[(tenant_id, user_id, new_device_id)]["epoch"] = old_epoch + 1
    add_edge("continuity", f"{tenant_id}:{user_id}:{old_device_id}:{old_epoch}", f"{tenant_id}:{user_id}:{new_device_id}:{old_epoch+1}", 0.95, "handoff_token")
    log("continuity_complete", "accepted", extra=body.model_dump())
    return {"ok": True, "new_epoch": old_epoch + 1}

@app.post("/v1/identity/recovery/request")
def recovery_request(body: RecoveryRequest):
    rid = f"recovery-{int(time.time()*1000)}"
    recovery_requests[rid] = {"tenant_id": body.tenant_id, "user_id": body.user_id, "target_device_id": body.target_device_id, "approvers": body.approvers, "approved_by": [], "status": "pending"}
    log("recovery_request", "accepted", extra={"recovery_id": rid, **body.model_dump()})
    return {"recovery_id": rid, "status": "pending"}

@app.post("/v1/identity/recovery/approve")
def recovery_approve(body: RecoveryApprove):
    if body.recovery_id not in recovery_requests:
        raise HTTPException(status_code=404, detail="recovery_not_found")
    rr = recovery_requests[body.recovery_id]
    if body.approver_device_id not in rr["approvers"]:
        raise HTTPException(status_code=403, detail="not_allowed")
    if body.approver_device_id not in rr["approved_by"]:
        rr["approved_by"].append(body.approver_device_id)
    if len(rr["approved_by"]) >= 2:
        rr["status"] = "approved"
    log("recovery_approve", "accepted", extra={"recovery_id": body.recovery_id, "approved_by": rr["approved_by"]})
    return rr

@app.post("/v1/verify/group")
def verify_group(body: GroupVerify):
    accepted, rejected = [], []
    for m in body.members:
        key = (body.tenant_id, m["user_id"], m["device_id"])
        st = states.get(key)
        if not st:
            rejected.append({"member": m, "reason": "no_state"})
            continue
        if st["stability"] >= body.min_stability and st["risk"] <= body.max_risk:
            accepted.append({"member": m, "state": st})
        else:
            rejected.append({"member": m, "reason": "policy_fail", "state": st})
    ok = len(accepted) >= body.require_quorum
    log("verify_group", "accepted" if ok else "rejected", "ok" if ok else "insufficient_quorum", extra={"accepted": len(accepted), "rejected": len(rejected)})
    return {"ok": ok, "accepted": accepted, "rejected": rejected, "require_quorum": body.require_quorum}

@app.get("/v1/graph/edges")
def get_edges():
    return {"edges": edges[-200:]}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    tpl = env.get_template("dashboard.html")
    return tpl.render(states=list(states.values())[-100:], edges=edges[-100:], audits=list(reversed(audits[-100:])))

