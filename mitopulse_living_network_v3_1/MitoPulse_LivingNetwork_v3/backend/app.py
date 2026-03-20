
from __future__ import annotations
import json, time, hashlib, math
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

def now() -> int:
    return int(time.time())

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def node_id(tenant: str, user: str, device: str, epoch: int) -> str:
    return f"{tenant}:{user}:{device}:{epoch}"

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def canonical_json(d: dict) -> bytes:
    return json.dumps(d, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")

def decay_weight(w: float, age_s: int, half_life_s: int = 3600) -> float:
    return float(w * (0.5 ** (max(age_s,0) / half_life_s)))

@dataclass
class Device:
    tenant_id: str
    user_id: str
    device_id: str
    pubkey_b64: str
    created_ts: int

@dataclass
class Baseline:
    mean: float = 0.55
    std: float = 0.08
    band: float = 0.15
    window_n: int = 0
    last_ts: int = 0
    dormant_since: Optional[int] = None

@dataclass
class IdentityEvent:
    ts: int
    tenant_id: str
    user_id: str
    device_id: str
    epoch: int
    tier: str
    idx: float
    stability: float
    human: float
    risk: int
    coercion: bool
    packet_hash: str
    meta: Dict[str, Any]

@dataclass
class Edge:
    type: str   # continuity / cohab / risk
    a: str
    b: str
    w: float
    ts: int
    meta: Dict[str, Any]

@dataclass
class Audit:
    ts: int
    action: str
    outcome: str
    reason: str
    meta: Dict[str, Any]

class DeviceRegisterIn(BaseModel):
    tenant_id: str = "demo"
    user_id: str
    device_id: str
    pubkey_b64: str

class ICPHandoffIn(BaseModel):
    tenant_id: str = "demo"
    user_id: str
    old_device_id: str
    new_device_id: str
    old_epoch: int = 1
    new_epoch: int = 2
    handoff_token_b64: str
    handoff_sig_b64: str

class ICPCompleteIn(BaseModel):
    tenant_id: str = "demo"
    user_id: str
    old_device_id: str
    new_device_id: str
    old_epoch: int = 1
    new_epoch: int = 2
    min_events_new: int = 2

class GroupMembershipIn(BaseModel):
    tenant_id: str = "demo"
    group_id: str
    user_id: str
    role: str = "member"

class GroupVerifyIn(BaseModel):
    tenant_id: str = "demo"
    group_id: str
    action: str
    accepted: List[str] = Field(default_factory=list)
    rejected: List[Dict[str, Any]] = Field(default_factory=list)
    policy: Dict[str, Any] = Field(default_factory=lambda: {"require_quorum": 2, "min_stability": 0.55, "max_risk": 60})

class RecoveryRequestIn(BaseModel):
    tenant_id: str = "demo"
    user_id: str
    lost_device_id: str
    new_device_id: str
    new_pubkey_b64: str
    group_id: str
    require_quorum: int = 2

class RecoveryApproveIn(BaseModel):
    tenant_id: str = "demo"
    group_id: str
    approver_user_id: str
    target_user_id: str
    request_id: str

class RecoveryCompleteIn(BaseModel):
    tenant_id: str = "demo"
    request_id: str

DEVICES: Dict[Tuple[str,str,str], Device] = {}
BASELINES: Dict[str, Baseline] = {}
EVENTS: List[IdentityEvent] = []
EDGES: List[Edge] = []
AUDIT: List[Audit] = []
GROUPS: Dict[Tuple[str,str], Dict[str,str]] = {}
RECOVERY: Dict[str, Dict[str, Any]] = {}

def robust_update(b: Baseline, idx: float, ts: int) -> Baseline:
    if b.last_ts and ts - b.last_ts > 7*24*3600:
        b.dormant_since = b.last_ts
    if b.dormant_since is not None:
        b.mean = 0.7*b.mean + 0.3*idx
        b.std = clamp(0.9*b.std + 0.1*abs(idx-b.mean), 0.03, 0.25)
    else:
        b.mean = 0.9*b.mean + 0.1*idx
        b.std = clamp(0.9*b.std + 0.1*abs(idx-b.mean), 0.03, 0.25)
    b.band = clamp(2.0*b.std, 0.08, 0.35)
    b.window_n = min(b.window_n+1, 2000)
    b.last_ts = ts
    b.dormant_since = None
    return b

def compute_stability(idx: float, b: Baseline) -> float:
    z = abs(idx - b.mean) / max(b.band, 1e-6)
    return clamp(1.0 - 0.9*z, 0.0, 1.0)

def compute_risk(stability: float, human: float, tier: str) -> int:
    tier_pen = {"tier0": 15, "tier1": 5, "tier2": 0}.get(tier, 10)
    base = 100*(1.0-stability)*0.8 + 100*(1.0-human)*0.2
    return int(clamp(base + tier_pen, 0, 100))

def verify_ed25519(tenant_id: str, user_id: str, device_id: str, raw: bytes, sig_b64: str):
    import base64
    dev = DEVICES.get((tenant_id, user_id, device_id))
    if not dev:
        raise HTTPException(status_code=401, detail="device_not_registered")
    try:
        vk = VerifyKey(base64.b64decode(dev.pubkey_b64))
    except Exception:
        raise HTTPException(status_code=500, detail="bad_pubkey")
    sig = base64.b64decode(sig_b64)
    try:
        vk.verify(raw, sig)
    except BadSignatureError:
        raise HTTPException(status_code=401, detail="bad_signature")

app = FastAPI(title="MitoPulse v3 — Living Network", version="3.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health():
    return {"status":"ok","ts":now()}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open("static/index.html","r",encoding="utf-8") as f:
        return f.read()

@app.post("/v3/device/register")
def device_register(inp: DeviceRegisterIn):
    DEVICES[(inp.tenant_id, inp.user_id, inp.device_id)] = Device(inp.tenant_id, inp.user_id, inp.device_id, inp.pubkey_b64, now())
    AUDIT.append(Audit(now(),"device_register","ok","ok",{"tenant":inp.tenant_id,"user":inp.user_id,"device":inp.device_id}))
    return {"status":"ok"}

@app.post("/v3/identity/event")
async def identity_event(req: Request):
    raw = await req.body()
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_json")
    sig = data.get("signature_b64")
    if not sig:
        raise HTTPException(status_code=422, detail="missing_signature_b64")
    tenant_id = data.get("tenant_id","demo")
    user_id = data.get("user_id")
    device_id = data.get("device_id")
    if not user_id or not device_id:
        raise HTTPException(status_code=422, detail="missing_user_or_device")
    
    # Verify signature: reconstruction of canonical message (sig removed)
    msg_dict = {k:v for k,v in data.items() if k != "signature_b64"}
    msg = canonical_json(msg_dict)
    verify_ed25519(tenant_id, user_id, device_id, msg, sig)

    epoch = int(data.get("epoch",1))
    ts = int(data.get("ts", now()))
    tier = data.get("tier","tier1")
    idx = float(data.get("idx", 0.5))
    human = float(data.get("human", 0.85))
    meta = data.get("meta", {}) or {}

    nid = node_id(tenant_id, user_id, device_id, epoch)
    b = BASELINES.get(nid, Baseline())
    b = robust_update(b, idx, ts)
    BASELINES[nid] = b

    stability = float(data.get("stability", compute_stability(idx,b)))
    stability = clamp(stability, 0.0, 1.0)
    risk = int(data.get("risk", compute_risk(stability, human, tier)))
    coercion = bool(data.get("coercion", False)) or (risk >= 90 and stability <= 0.45)

    packet_hash = sha256_hex(raw)
    EVENTS.append(IdentityEvent(ts, tenant_id, user_id, device_id, epoch, tier, idx, stability, human, risk, coercion, packet_hash, meta))
    AUDIT.append(Audit(now(),"identity_event","ok","ok",{"packet_hash":packet_hash}))

    if coercion or risk >= 85:
        EDGES.append(Edge("risk", nid, f"{tenant_id}:RISK", clamp(risk/100.0,0.5,0.98), ts, {"reason":"coercion_or_high_risk"}))

    # co-occurrence cohab edges (last 6 unique nodes)
    recent=[]
    for e in EVENTS[-6:]:
        if e.tenant_id==tenant_id:
            recent.append(node_id(e.tenant_id,e.user_id,e.device_id,e.epoch))
    seen=set(); recent_u=[]
    for x in recent:
        if x not in seen:
            seen.add(x); recent_u.append(x)
    for i in range(len(recent_u)):
        for j in range(i+1,len(recent_u)):
            EDGES.append(Edge("cohab", recent_u[i], recent_u[j], 0.35, ts, {"reason":"co_occurrence"}))

    return {"status":"ok","packet_hash":packet_hash,"node":nid}

@app.get("/v3/identity/state")
def identity_state(tenant_id: str, user_id: str, device_id: str, epoch: int = 1):
    nid = node_id(tenant_id,user_id,device_id,epoch)
    b = BASELINES.get(nid)
    if not b:
        raise HTTPException(status_code=404, detail="no_state")
    return {"node":nid,"baseline":asdict(b)}

@app.post("/v3/group/membership")
def group_membership(inp: GroupMembershipIn):
    GROUPS.setdefault((inp.tenant_id, inp.group_id), {})[inp.user_id]=inp.role
    AUDIT.append(Audit(now(),"group_membership","ok","ok",{"group_id":inp.group_id,"user_id":inp.user_id,"role":inp.role}))
    return {"status":"ok"}

@app.post("/v3/verify/group")
def verify_group(inp: GroupVerifyIn):
    require_quorum = int(inp.policy.get("require_quorum",2))
    min_stability = float(inp.policy.get("min_stability",0.55))
    max_risk = int(inp.policy.get("max_risk",60))
    ok_users=[]; rejected=[]
    for u in inp.accepted:
        last = next((e for e in reversed(EVENTS) if e.tenant_id==inp.tenant_id and e.user_id==u), None)
        if not last:
            rejected.append({"user_id":u,"reason":"no_events"}); continue
        if last.stability < min_stability:
            rejected.append({"user_id":u,"reason":"low_stability"}); continue
        if last.risk > max_risk:
            rejected.append({"user_id":u,"reason":"high_risk"}); continue
        ok_users.append(u)
    if len(ok_users) < require_quorum:
        AUDIT.append(Audit(now(),"verify_group","fail","insufficient_quorum",{"group_id":inp.group_id,"action":inp.action,"accepted":ok_users,"rejected":rejected,"policy":inp.policy}))
        return JSONResponse(status_code=200, content={"status":"fail","reason":"insufficient_quorum","accepted":ok_users,"rejected":rejected,"policy":inp.policy})
    AUDIT.append(Audit(now(),"verify_group","ok","ok",{"group_id":inp.group_id,"action":inp.action,"accepted":ok_users,"policy":inp.policy}))
    return {"status":"ok","accepted":ok_users,"policy":inp.policy}

@app.post("/v3/icp/handoff")
def icp_handoff(inp: ICPHandoffIn):
    import base64
    token = base64.b64decode(inp.handoff_token_b64)
    sig = base64.b64decode(inp.handoff_sig_b64)
    dev = DEVICES.get((inp.tenant_id, inp.user_id, inp.old_device_id))
    if not dev:
        raise HTTPException(status_code=401, detail="old_device_not_registered")
    vk = VerifyKey(base64.b64decode(dev.pubkey_b64))
    try:
        vk.verify(token, sig)
    except BadSignatureError:
        raise HTTPException(status_code=401, detail="bad_handoff_sig")
    AUDIT.append(Audit(now(),"icp_handoff","ok","ok",{"old_device":inp.old_device_id,"new_device":inp.new_device_id,"handoff_hash":sha256_hex(token)}))
    return {"status":"ok","handoff_hash":sha256_hex(token)}

@app.post("/v3/icp/complete")
def icp_complete(inp: ICPCompleteIn):
    old_node = node_id(inp.tenant_id, inp.user_id, inp.old_device_id, inp.old_epoch)
    new_node = node_id(inp.tenant_id, inp.user_id, inp.new_device_id, inp.new_epoch)
    cnt = sum(1 for e in EVENTS if e.tenant_id==inp.tenant_id and e.user_id==inp.user_id and e.device_id==inp.new_device_id and e.epoch==inp.new_epoch)
    if cnt < inp.min_events_new:
        AUDIT.append(Audit(now(),"icp_complete","fail","insufficient_new_events",{"old_node":old_node,"new_node":new_node,"count":cnt}))
        return {"status":"fail","reason":"insufficient_new_events","count":cnt}
    EDGES.append(Edge("continuity", old_node, new_node, 0.92, now(), {"reason":"handoff_token"}))
    AUDIT.append(Audit(now(),"icp_complete","ok","ok",{"old_node":old_node,"new_node":new_node}))
    return {"status":"ok","old_node":old_node,"new_node":new_node}

@app.post("/v3/recovery/request")
def recovery_request(inp: RecoveryRequestIn):
    rid = sha256_hex(f"{inp.tenant_id}:{inp.user_id}:{inp.lost_device_id}:{inp.new_device_id}:{now()}".encode())
    RECOVERY[rid] = {
        "tenant_id": inp.tenant_id,
        "user_id": inp.user_id,
        "lost_device_id": inp.lost_device_id,
        "new_device_id": inp.new_device_id,
        "new_pubkey_b64": inp.new_pubkey_b64,
        "group_id": inp.group_id,
        "require_quorum": int(inp.require_quorum),
        "approvals": set(),
        "status": "pending",
    }
    AUDIT.append(Audit(now(),"recovery_request","ok","ok",{"request_id":rid,"group_id":inp.group_id}))
    return {"status":"ok","request_id":rid}

@app.post("/v3/recovery/approve")
def recovery_approve(inp: RecoveryApproveIn):
    r = RECOVERY.get(inp.request_id)
    if not r: raise HTTPException(status_code=404, detail="no_such_request")
    members = GROUPS.get((inp.tenant_id, inp.group_id), {})
    if inp.approver_user_id not in members:
        raise HTTPException(status_code=403, detail="approver_not_in_group")
    r["approvals"].add(inp.approver_user_id)
    AUDIT.append(Audit(now(),"recovery_approve","ok","ok",{"request_id":inp.request_id,"approver":inp.approver_user_id}))
    return {"status":"ok","approvals":sorted(list(r["approvals"]))}

@app.post("/v3/recovery/complete")
def recovery_complete(inp: RecoveryCompleteIn):
    r = RECOVERY.get(inp.request_id)
    if not r: raise HTTPException(status_code=404, detail="no_such_request")
    if r["status"] != "pending":
        return {"status":"fail","reason":"not_pending","state":r["status"]}
    if len(r["approvals"]) < int(r["require_quorum"]):
        AUDIT.append(Audit(now(),"recovery_complete","fail","insufficient_quorum",{"request_id":inp.request_id,"approvals":len(r["approvals"])}))
        return {"status":"fail","reason":"insufficient_quorum","approvals":sorted(list(r["approvals"]))}
    DEVICES[(r["tenant_id"], r["user_id"], r["new_device_id"])] = Device(r["tenant_id"], r["user_id"], r["new_device_id"], r["new_pubkey_b64"], now())
    r["status"]="completed"
    AUDIT.append(Audit(now(),"recovery_complete","ok","ok",{"request_id":inp.request_id,"new_device":r["new_device_id"]}))
    return {"status":"ok","new_device_id":r["new_device_id"]}

@app.get("/v3/events/latest")
def events_latest(tenant_id: str="demo", limit: int=40):
    out=[]
    for e in list(reversed(EVENTS))[:max(1,min(limit,200))]:
        if e.tenant_id!=tenant_id: continue
        out.append({
            "ts": e.ts, "tenant": e.tenant_id, "user": e.user_id, "device": e.device_id, "epoch": e.epoch,
            "tier": e.tier, "idx": round(e.idx,3), "stability": round(e.stability,3), "human": round(e.human,2),
            "risk": e.risk, "coercion": "COERCION" if e.coercion else "OK", "packet_hash": e.packet_hash[:16]+"…"
        })
    return {"rows": out}

@app.get("/v3/audit/latest")
def audit_latest(limit: int=45):
    out=[]
    for a in list(reversed(AUDIT))[:max(1,min(limit,200))]:
        out.append({"ts":a.ts,"action":a.action,"outcome":a.outcome,"reason":a.reason,"meta":a.meta})
    return {"rows": out}

@app.get("/v3/graph/snapshot")
def graph_snapshot(tenant_id: str="demo"):
    t = now()
    edges=[]
    for e in EDGES[-250:]:
        if not (e.a.startswith(tenant_id+":") or e.b.startswith(tenant_id+":")):
            continue
        w = decay_weight(e.w, t-int(e.ts))
        if w < 0.05: continue
        edges.append({"type":e.type,"a":e.a,"b":e.b,"w":round(w,3),"ts":e.ts,"meta":e.meta})

    work={"demo":[]}; attack=[]
    for ev in EVENTS[-60:]:
        if ev.tenant_id!=tenant_id: continue
        nid = node_id(ev.tenant_id, ev.user_id, ev.device_id, ev.epoch)
        if ev.coercion or ev.risk>=90:
            attack.append(nid)
        else:
            if tenant_id=="demo" and nid not in work["demo"]:
                work["demo"].append(nid)
    clusters={"work":work,"attack":list(dict.fromkeys(attack))[:20]}
    return {"edges":edges,"clusters":clusters,"ts":t}
