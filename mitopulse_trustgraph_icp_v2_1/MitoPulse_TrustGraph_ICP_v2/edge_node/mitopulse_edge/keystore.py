
from __future__ import annotations
from pathlib import Path
import base64, json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

STORE = Path(__file__).resolve().parent / ".keystore"

def ensure_store():
    STORE.mkdir(parents=True, exist_ok=True)

def key_path(device_id: str) -> Path:
    return STORE / f"{device_id}.ed25519"

def load_or_create(device_id: str) -> Ed25519PrivateKey:
    ensure_store()
    p = key_path(device_id)
    if p.exists():
        b = base64.b64decode(p.read_text().strip())
        return Ed25519PrivateKey.from_private_bytes(b)
    priv = Ed25519PrivateKey.generate()
    raw = priv.private_bytes_raw()
    p.write_text(base64.b64encode(raw).decode("utf-8"))
    return priv
