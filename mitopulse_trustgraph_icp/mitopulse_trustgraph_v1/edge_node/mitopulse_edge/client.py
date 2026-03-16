from __future__ import annotations

import json
from typing import Dict, Any

import requests


class MitoPulseGatewayClient:
    def __init__(self, base_url: str, tenant_id: str, api_key: str):
        self.base = base_url.rstrip("/")
        self.tenant_id = tenant_id
        self.api_key = api_key

    def post_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(
            f"{self.base}/v1/proof-packets",
            json=packet,
            headers={"x-api-key": self.api_key},
            timeout=20,
        )
        return {"status": r.status_code, "json": r.json()}

    def icp_start(self, body: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(
            f"{self.base}/v1/icp/handoff/start",
            json=body,
            headers={"x-api-key": self.api_key},
            timeout=20,
        )
        return {"status": r.status_code, "json": r.json()}

    def icp_complete(self, body: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(
            f"{self.base}/v1/icp/handoff/complete",
            json=body,
            headers={"x-api-key": self.api_key},
            timeout=20,
        )
        return {"status": r.status_code, "json": r.json()}
