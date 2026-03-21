from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class EntityObject:
    entity_id: str
    entity_type: str
    identity_state: str
    evidence_score: float
    behavior_signature: Dict[str, Any] = field(default_factory=dict)
    relational_position: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrustProfile:
    entity_id: str
    trust_score: float
    trust_velocity: float
    trust_volatility: float
    trust_reserve: float
    trust_state: str

@dataclass
class RiskProfile:
    nhi: float
    tpi: float
    scr: float
    mdi: float
    risk_state: str

@dataclass
class ValidationProfile:
    confidence: float
    quorum_score: float
    validated: bool
    challenged: bool = False
    challenge_window_open: bool = False
    notes: List[str] = field(default_factory=list)

@dataclass
class PolicyObject:
    policy_id: str
    name: str
    condition_text: str
    action_text: str
    confidence_required: float
    quorum_required: float
    severity_band: str
    enabled: int
    version: int
    explanation: str

@dataclass
class ActionObject:
    action_id: str
    target_id: str
    action_type: str
    approved: bool
    explanation: str
    policy_id: Optional[str] = None

@dataclass
class RecoveryProfile:
    recovery_state: str
    stability_score: float
    reintegration_ready: bool

@dataclass
class FederationAnchor:
    anchor_id: str
    system_name: str
    trust_weight: float
    status: str
