import requests

class MitoPulseDeveloperClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def health(self):
        return requests.get(f"{self.base_url}/health", timeout=10).json()

    def send_presence(self, payload: dict, tenant_header: str | None = None, idempotency_key: str | None = None):
        headers = {}
        if tenant_header:
            headers["X-Tenant-Id"] = tenant_header
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return requests.post(f"{self.base_url}/v2/presence/event", json=payload, headers=headers, timeout=10).json()

    def state(self, tenant_id: str, user_id: str, device_id: str):
        return requests.get(f"{self.base_url}/v2/identity/state", params={"tenant_id": tenant_id, "user_id": user_id, "device_id": device_id}, timeout=10).json()
