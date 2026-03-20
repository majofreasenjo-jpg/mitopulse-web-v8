
import json, time, base64
from typing import Dict, Any
from nacl.signing import SigningKey
import requests

def canonical_json(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")

class MitoPulseEdgeClient:
    def __init__(self, base_url: str, tenant_id: str, user_id: str, device_id: str):
        self.base_url = base_url.rstrip("/")
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.device_id = device_id
        self.signing_key = SigningKey.generate()
        self.public_key_b64 = base64.b64encode(bytes(self.signing_key.verify_key)).decode()

    def register(self):
        payload = {"tenant_id": self.tenant_id, "user_id": self.user_id, "device_id": self.device_id, "public_key": self.public_key_b64}
        return requests.post(f"{self.base_url}/v1/devices/register", json=payload, timeout=15).json()

    def sign_packet(self, packet: Dict[str, Any]) -> str:
        sig = self.signing_key.sign(canonical_json(packet)).signature
        return base64.b64encode(sig).decode()

    def send_presence(self, tier: str, index: float, stability: float, human_conf: float, risk: int, coercion: bool, context: Dict[str, Any] | None = None):
        packet = {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "ts": int(time.time()),
            "request_id": f"{self.device_id}-{int(time.time()*1000)}",
            "epoch": 1,
            "tier": tier,
            "index": index,
            "stability": stability,
            "human_conf": human_conf,
            "risk": risk,
            "coercion": coercion,
            "context": context or {}
        }
        payload = dict(packet)
        payload["signature"] = self.sign_packet(packet)
        return requests.post(f"{self.base_url}/v1/presence/event", json=payload, timeout=15).json()
