from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class MitoPulseClient:
    """Tiny client for the verifier backend."""

    base_url: str = "http://127.0.0.1:8000"
    timeout_s: float = 10.0

    def post_identity_event(
        self,
        *,
        user_id: str,
        device_id: str,
        ts: int,
        dynamic_id: str,
        mitopulse_index: float,
        slope: float,
        tier: str = "tier1",
        event_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "event_id": event_id or str(uuid.uuid4()),
            "user_id": user_id,
            "device_id": device_id,
            "ts": int(ts),
            "dynamic_id": dynamic_id,
            "mitopulse_index": float(mitopulse_index),
            "slope": float(slope),
            "tier": tier,
        }
        r = requests.post(f"{self.base_url}/v1/identity-events", json=payload, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()

    def verify(
        self,
        *,
        user_id: str,
        device_id: str,
        dynamic_id: str,
        ts: Optional[int] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "request_id": request_id or str(uuid.uuid4()),
            "user_id": user_id,
            "device_id": device_id,
            "ts": int(ts or time.time()),
            "dynamic_id": dynamic_id,
        }
        r = requests.post(f"{self.base_url}/v1/verify", json=payload, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()
