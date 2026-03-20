
import requests

class MitoPulseClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def evaluate(self, entity, signal):
        response = requests.post(
            f"{self.base_url}/evaluate",
            json={"entity": entity, "signal": signal}
        )
        return response.json()
