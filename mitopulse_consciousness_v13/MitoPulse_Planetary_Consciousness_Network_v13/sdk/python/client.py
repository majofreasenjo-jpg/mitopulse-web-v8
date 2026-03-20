import requests

class MitoPulseConsciousness:

    def __init__(self,base_url):
        self.base_url = base_url

    def signal(self,data):
        r = requests.post(f"{self.base_url}/v13/signal", json=data)
        return r.json()
