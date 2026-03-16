
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal

Tier = Literal["tier0","tier1","tier2","tier3"]

class Signals(BaseModel):
    hr: float = Field(..., ge=0)
    hrv_rmssd: Optional[float] = Field(None, ge=0)
    spo2: Optional[float] = Field(None, ge=0, le=1.0)
    sleep_score: Optional[float] = Field(None, ge=0, le=1.0)
    load: Optional[float] = Field(None, ge=0)
    # Tier0 support (basic phone / no wearable): interaction proxies
    tap_rate: Optional[float] = Field(None, ge=0)       # taps/min
    keystroke_var: Optional[float] = Field(None, ge=0)  # variability proxy

class Env(BaseModel):
    altitude_m: Optional[float] = None
    temp_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    pressure_hpa: Optional[float] = None

class ProofPacket(BaseModel):
    version: str = "2.0"
    tenant_id: str
    user_id: str
    device_id: str
    epoch: int
    ts: int
    tier: Tier
    signals: Signals
    env: Env
    idx: float
    slope: float
    stability: float
    human_conf: float
    risk: int
    coercion: bool
    request_id: str
    # Ed25519 signature over canonical JSON
    sig_b64: str

class VerifyRequest(BaseModel):
    tenant_id: str
    user_id: str
    device_id: str
    epoch: int
    ts: int
    request_id: str
    packet_hash: str

class GroupVerifyRequest(BaseModel):
    tenant_id: str
    group_id: str
    # event to authorize (opaque to backend; shown in audit)
    action: str
    # a list of (user_id, device_id, epoch, request_id, packet_hash, ts)
    proofs: List[VerifyRequest]

class DeviceRegisterRequest(BaseModel):
    tenant_id: str
    user_id: str
    device_id: str
    pubkey_b64: str

class TenantUpsertRequest(BaseModel):
    tenant_id: str
    name: str
    policy: Dict[str, Any]

class GroupMembershipRequest(BaseModel):
    tenant_id: str
    group_id: str
    user_id: str
    role: str = "member"

class IdentityStateResponse(BaseModel):
    user_id: str
    device_id: str
    epoch: int
    last_ts: int
    mean_idx: float
    std_idx: float
    stability_band: float
    hibernating: bool
