
import requests
import hashlib
import hmac
import base64
import time
from typing import Dict, Any, Optional

class MitoPulseClient:
    def __init__(self, base_url="http://127.0.0.1:8000", server_secret="server_secret"):
        self.base_url = base_url
        self.secret = server_secret.encode()

    def _generate_signature(self, user_id, device_id, ts, dynamic_id):
        payload = f"{user_id}:{device_id}:{ts}:{dynamic_id}".encode()
        mac = hmac.new(self.secret, payload, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(mac).decode().rstrip("=")

    def post_identity_event(self, user_id, device_id, ts, dynamic_id, tier, signature=None):
        if signature is None:
            signature = self._generate_signature(user_id, device_id, ts, dynamic_id)
        
        payload = {
            "user_id": user_id,
            "device_id": device_id,
            "ts": ts,
            "dynamic_id": dynamic_id,
            "tier": tier,
            "signature": signature
        }
        r = requests.post(f"{self.base_url}/v1/identity-events", json=payload)
        r.raise_for_status()
        return r.json()

    def verify(self, user_id, device_id, ts, dynamic_id, tier="tier1"):
        # Note: v0.4.0 backend expects a full IdentityEvent for verification
        signature = self._generate_signature(user_id, device_id, ts, dynamic_id)
        payload = {
            "user_id": user_id,
            "device_id": device_id,
            "ts": ts,
            "dynamic_id": dynamic_id,
            "tier": tier,
            "signature": signature
        }
        r = requests.post(f"{self.base_url}/v1/verify", json=payload)
        r.raise_for_status()
        return r.json()
