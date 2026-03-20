from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidatorNode:
    node_id: str
    label: str
    trust_weight: float
    active: bool = True


@dataclass
class Vote:
    node_id: str
    decision: str
    confidence: float
    reason: Optional[str] = None
