import requests

class MitoPulseClient:

    def __init__(self, base_url, api_key):
        self.base = base_url
        self.key = api_key

    def health(self):
        return requests.get(f"{self.base}/v3/healthcheck").json()

    def send_presence(self, payload):
        return requests.post(
            f"{self.base}/v3/presence",
            json=payload,
            headers={"X-API-Key": self.key}
        ).json()
