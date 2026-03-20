
import base64, json, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def canonical_json(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def verify_ed25519(pub_b64: str, msg: bytes, sig_b64: str) -> bool:
    try:
        pub = base64.b64decode(pub_b64)
        sig = base64.b64decode(sig_b64)
        pk = Ed25519PublicKey.from_public_bytes(pub)
        pk.verify(sig, msg)
        return True
    except Exception:
        return False
