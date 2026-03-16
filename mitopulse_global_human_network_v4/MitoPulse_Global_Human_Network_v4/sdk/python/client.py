import requests

class MitoPulseGlobalClient:
    def __init__(self, base_url: str, api_key: str, region: str = "latam-south"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.region = region

    def health(self):
        return requests.get(f"{self.base_url}/v4/healthcheck", timeout=10).json()

    def send_presence(self, payload: dict, idempotency_key: str | None = None):
        headers = {"X-API-Key": self.api_key, "X-Region": self.region}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return requests.post(f"{self.base_url}/v4/presence", json=payload, headers=headers, timeout=15).json()
