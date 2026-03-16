from __future__ import annotations

import base64
import hmac
import hashlib
from typing import Optional


def hmac_sha256_b64(secret_b64: str, message: bytes) -> str:
    key = base64.b64decode(secret_b64)
    mac = hmac.new(key, message, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode("utf-8").rstrip("=")


def constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)
