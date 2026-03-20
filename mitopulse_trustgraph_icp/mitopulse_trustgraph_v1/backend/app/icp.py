from __future__ import annotations

import json
import time
from typing import Dict

from .security import hmac_sha256_b64, constant_time_equal, b64url_encode, b64url_decode


def build_handoff_token(payload: Dict, secret_b64: str) -> str:
    """Token signed by old device to authorize continuity to a new device."""
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    sig = hmac_sha256_b64(secret_b64, body)
    token = {"p": payload, "s": sig}
    return b64url_encode(json.dumps(token, separators=(",", ":")).encode("utf-8"))


def verify_handoff_token(token_b64: str, secret_b64: str) -> Dict:
    raw = b64url_decode(token_b64)
    token = json.loads(raw.decode("utf-8"))
    payload = token["p"]
    sig = token["s"]
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    expect = hmac_sha256_b64(secret_b64, body)
    if not constant_time_equal(sig, expect):
        raise ValueError("invalid_handoff_sig")
    return payload
