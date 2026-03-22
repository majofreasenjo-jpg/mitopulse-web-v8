from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ExecutiveState(BaseModel):
    tick: int
    state: str
    nhi: float
    tpi: float
    scr: float
    aci: float
    avs: float
    metabolic_load: float
    homeostasis_stability: float
    reflex_activation_count: int
    behavioral_predation_index: float
    cycle_recurrence_risk: float
    fdi: float
    ssi: float
    cfi: float
    fpi: float
    sei: float
    msi: float
    pmi: float
    aes: float
    collapse_probability: float
    time_to_criticality: float
    confidence_low: float
    confidence_high: float
    top_drivers: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    explanation: str = ""

class ProtocolSnapshot(BaseModel):
    protocol_state: str
    identity_state: str
    crypto_state: str
    autopoietic_state: str
    drivers: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

class GraphNode(BaseModel):
    id: str
    role: str
    risk: float
    coherence: float
    zone: str

class ApiPayload(BaseModel):
    raw: Dict[str, Any]
    state: ExecutiveState
    protocol: ProtocolSnapshot
    graph: List[GraphNode]
