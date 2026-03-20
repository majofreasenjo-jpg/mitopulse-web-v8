from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time

from engines.presence import PresenceEngine
from engines.risk import RiskEngine
from services.ledger import LedgerService

router = APIRouter()

# Instantiate Core Services (In a real app, inject these via dependency injection)
presence_engine = PresenceEngine()
risk_engine = RiskEngine()
ledger_service = LedgerService()

# API Models
class VerifyRequest(BaseModel):
    tenant_id: str
    device_id: str
    timestamp: float
    nonce: str
    signature: str
    context: Optional[Dict[str, Any]] = None  # e.g., tx_amount, action_type, location

class VerifyResponse(BaseModel):
    verified: bool
    confidence: float
    risk_level: str
    transaction_id: str

@router.post("/verify", response_model=VerifyResponse)
async def verify_human_presence(req: VerifyRequest):
    """
    Core B2B API Endpoint for Human Presence Verification.
    Called by the client's backend during a critical operation.
    """
    # 1. Presence Engine (Cryptographic Identity & Anti-Replay)
    is_valid_crypto = presence_engine.verify_signature(
        device_id=req.device_id,
        timestamp=req.timestamp,
        nonce=req.nonce,
        signature=req.signature
    )
    
    if not is_valid_crypto:
        ledger_service.record_event(req.tenant_id, req.device_id, "VERIFY_FAILED", "Cryptographic signature mismatch")
        raise HTTPException(status_code=401, detail="Cryptographic verification failed")

    # Anti-replay check based on timestamp
    current_time = time.time()
    if abs(current_time - req.timestamp) > 300: # 5 min tolerance
        ledger_service.record_event(req.tenant_id, req.device_id, "VERIFY_FAILED", "Stale timestamp (replay block)")
        raise HTTPException(status_code=401, detail="Request expired")

    # 2. Risk Engine (Baseline Drift & Coercion Detection)
    risk_assessment = risk_engine.evaluate_risk(req.device_id, req.context)
    
    # 3. Decision Logic
    confidence_score = 1.0 - (risk_assessment['risk_score'] / 100)
    is_verified = confidence_score > 0.7
    
    status_label = "VERIFY_SUCCESS" if is_verified else "VERIFY_FLAGGED"
    details = f"Confidence: {confidence_score:.2f}, Risk: {risk_assessment['level']}"
    
    # 4. Immutable Ledger Audit
    tx_id = ledger_service.record_event(req.tenant_id, req.device_id, status_label, details)

    return VerifyResponse(
        verified=is_verified,
        confidence=confidence_score,
        risk_level=risk_assessment['level'],
        transaction_id=tx_id
    )
