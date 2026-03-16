
import json, time, hashlib, base64
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional, Tuple

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Using PyNaCl for Ed25519
try:
    from nacl.signing import VerifyKey
    from nacl.exceptions import BadSignatureError
except ImportError:
    # Fallback for systems without PyNaCl for basic logic flow
    VerifyKey = None

# --- UTILS ---
def now() -> int:
    return int(time.time())

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_json(d: dict) -> bytes:
    # Deterministic JSON for signature verification
    return json.dumps(d, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")

# --- DATA MODELS ---

@dataclass
class Device:
    tenant_id: str
    user_id: str
    device_id: str
    pubkey_b64: str
    created_ts: int

@dataclass
class IdentityEvent:
    ts: int
    user_id: str
    device_id: str
    epoch: int
    stability: float
    human_conf: float
    risk: int
    region: str
    packet_hash: str

@dataclass
class Edge:
    type: str   # continuity / trust / risk
    a: str
    b: str
    weight: float
    ts: int

@dataclass
class AuditLog:
    ts: int
    action: str
    status: str
    details: str

# --- STATE (IN-MEMORY FOR DEMO) ---
DEVICES: Dict[str, Device] = {} # key: user_id:device_id
EVENTS: List[IdentityEvent] = []
EDGES: List[Edge] = []
AUDIT: List[AuditLog] = []
ICP_HANDOFFS: Dict[str, Dict] = {} # user_id -> handoff_data

# --- API MODELS ---
class RegisterIn(BaseModel):
    user_id: str
    device_id: str
    pubkey_b64: str

class EventIn(BaseModel):
    user_id: str
    device_id: str
    epoch: int
    stability: float
    human_conf: float
    risk: int
    region: str = "Global"
    signature_b64: str

class ICPHandoffIn(BaseModel):
    user_id: str
    old_device_id: str
    new_device_id: str
    token_b64: str
    signature_b64: str

# --- APP ---
app = FastAPI(title="MitoPulse v22 — Identity Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "version": "22.0.1", "ts": now()}

@app.post("/v22/device/register")
def register_device(inp: RegisterIn):
    key = f"{inp.user_id}:{inp.device_id}"
    DEVICES[key] = Device(
        tenant_id="master_demo",
        user_id=inp.user_id,
        device_id=inp.device_id,
        pubkey_b64=inp.pubkey_b64,
        created_ts=now()
    )
    AUDIT.append(AuditLog(now(), "REGISTER", "OK", f"Node created: {key}"))
    return {"status": "ok", "message": "Device anchored to network."}

@app.post("/v22/identity/pulse")
async def identity_pulse(req: Request):
    try:
        raw = await req.body()
        data = json.loads(raw)
    except Exception:
        raise HTTPException(400, "Invalid JSON.")
    
    user_id = data.get("user_id")
    device_id = data.get("device_id")
    sig_b64 = data.get("signature_b64")
    
    if not all([user_id, device_id, sig_b64]):
        raise HTTPException(422, "Missing identity parameters.")
    
    device_key = f"{user_id}:{device_id}"
    device = DEVICES.get(device_key)
    if not device:
        raise HTTPException(401, "Device not registered.")

    # RECONSTRUCT MESSAGE FOR SIG VERIFY
    # Remove signature from data for canonical hash
    msg_dict = {k:v for k,v in data.items() if k != "signature_b64"}
    msg_bytes = canonical_json(msg_dict)
    
    # SIGNATURE VERIFICATION
    if VerifyKey:
        try:
            vk = VerifyKey(base64.b64decode(device.pubkey_b64))
            vk.verify(msg_bytes, base64.b64decode(sig_b64))
        except (BadSignatureError, Exception) as e:
            AUDIT.append(AuditLog(now(), "PULSE", "FAIL", f"Sig verification failed for {user_id}: {str(e)}"))
            # In demo mode, we might allow bypass if specifically configured, but here we enforce
            raise HTTPException(401, f"Invalid packet signature: {str(e)}")
    else:
        # Mock verification for environments without PyNaCl
        AUDIT.append(AuditLog(now(), "PULSE", "WARN", f"PyNaCl missing: bypassed sig check for {user_id}"))

    # PROCESS EVENT
    event = IdentityEvent(
        ts=data.get("ts", now()),
        user_id=user_id,
        device_id=device_id,
        epoch=data.get("epoch", 1),
        stability=float(data.get("stability", 0.95)),
        human_conf=float(data.get("human_conf", 1.0)),
        risk=int(data.get("risk", 0)),
        region=data.get("region", "Global"),
        packet_hash=sha256_hex(msg_bytes)
    )
    EVENTS.append(event)
    
    # Update Trust Graph
    # user node, device node, and edge between them
    u_node = f"user:{user_id}"
    d_node = f"node:{device_key}"
    EDGES.append(Edge("pulse", u_node, d_node, event.stability, now()))
    
    # Audit
    if len(AUDIT) > 100: AUDIT.pop(0)
    AUDIT.append(AuditLog(now(), "PULSE", "OK", f"Verified heartbeat: {user_id} (hash: {event.packet_hash[:8]})"))
    
    return {"status": "ok", "packet_hash": event.packet_hash, "node": d_node}

@app.post("/v22/icp/init")
def icp_init(inp: ICPHandoffIn):
    # Old device signs a handoff token for the new device
    device_key = f"{inp.user_id}:{inp.old_device_id}"
    device = DEVICES.get(device_key)
    if not device: raise HTTPException(401, "Source device not found.")
    
    token_bytes = base64.b64decode(inp.token_b64)
    sig_bytes = base64.b64decode(inp.signature_b64)
    
    if VerifyKey:
        try:
            vk = VerifyKey(base64.b64decode(device.pubkey_b64))
            vk.verify(token_bytes, sig_bytes)
        except:
            raise HTTPException(401, "Invalid handoff signature.")

    token_hash = sha256_hex(token_bytes)
    ICP_HANDOFFS[inp.user_id] = {
        "old_device": inp.old_device_id,
        "new_device": inp.new_device_id,
        "token_hash": token_hash,
        "ts": now()
    }
    
    AUDIT.append(AuditLog(now(), "ICP_INIT", "OK", f"Continuity token registered for {inp.user_id}"))
    return {"status": "ok", "continuity_hash": token_hash}

@app.post("/v22/icp/complete")
def icp_complete(user_id: str, new_device_id: str):
    handoff = ICP_HANDOFFS.get(user_id)
    if not handoff or handoff["new_device"] != new_device_id:
        raise HTTPException(404, "No pending handoff found.")
    
    # Create Continuity Edge in Graph
    u_node = f"user:{user_id}"
    EDGES.append(Edge("continuity", handoff["old_device"], handoff["new_device"], 0.99, now()))
    EDGES.append(Edge("pulse", u_node, f"node:{user_id}:{new_device_id}", 0.99, now()))
    
    AUDIT.append(AuditLog(now(), "ICP_DONE", "OK", f"Identity migrated to {new_device_id}"))
    del ICP_HANDOFFS[user_id]
    return {"status": "ok"}

@app.get("/v22/graph/snapshot")
def graph_snapshot():
    # Decay logic for edges: simple linear for demo
    t = now()
    filtered_edges = []
    nodes_set = set()
    
    for e in EDGES[-300:]:
        age = t - e.ts
        weight = e.weight * (0.9 ** (age / 60)) # decay every minute
        if weight > 0.05:
            filtered_edges.append({
                "source": e.a,
                "target": e.b,
                "weight": round(weight, 3),
                "type": e.type
            })
            nodes_set.add(e.a)
            nodes_set.add(e.b)
    
    return {
        "nodes": [{"id": n, "type": "user" if n.startswith("user:") else "node"} for n in nodes_set],
        "links": filtered_edges,
        "metrics": {
            "total_nodes": len(DEVICES),
            "total_pulses": len(EVENTS),
            "living_edges": len(filtered_edges)
        }
    }

@app.get("/v22/audit/latest")
def audit_latest():
    return {"rows": [asdict(a) for a in reversed(AUDIT[-100:])]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
