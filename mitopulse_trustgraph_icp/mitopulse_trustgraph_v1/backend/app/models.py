from __future__ import annotations

from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

Tier = Literal["tier0", "tier1", "tier2", "tier3"]


class Signals(BaseModel):
    hr: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    spo2: Optional[float] = None
    sleep_score: Optional[float] = None
    load: Optional[float] = None
    # Tier0 allows none


class Env(BaseModel):
    altitude_m: Optional[float] = None
    temp_c: Optional[float] = None
    humidity: Optional[float] = None
    pressure_hpa: Optional[float] = None


class ProofPacket(BaseModel):
    tenant_id: str
    user_id: str
    device_id: str
    epoch: int = 1

    request_id: str
    ts: int

    tier_used: Tier
    index_value: float
    dynamic_id: str

    risk: int = Field(ge=0, le=100)
    coercion: bool
    stability: float = Field(ge=0.0, le=1.0)
    human_conf: float = Field(ge=0.0, le=1.0)

    context_fp: Optional[str] = None

    # signed envelope
    payload: Dict[str, Any]
    sig: str


class VerifyResponse(BaseModel):
    verdict: Literal["ok", "suspicious", "fail"]
    reason: str


class RegisterTenantRequest(BaseModel):
    tenant_id: str
    name: str


class RegisterDeviceRequest(BaseModel):
    tenant_id: str
    user_id: str
    device_id: str
    shared_secret_b64: str
    tier_hint: Optional[str] = None


class HandoffStartRequest(BaseModel):
    tenant_id: str
    user_id: str
    old_device_id: str
    new_device_id: str
    request_id: str
    ts: int
    payload: Dict[str, Any]
    sig: str


class HandoffCompleteRequest(BaseModel):
    tenant_id: str
    user_id: str
    new_device_id: str
    handoff_token: str
    request_id: str
    ts: int
    payload: Dict[str, Any]
    sig: str
