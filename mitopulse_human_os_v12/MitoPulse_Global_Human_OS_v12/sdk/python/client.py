import requests

class MitoPulseHumanOS:

    def __init__(self,base_url):
        self.base_url = base_url

    def presence(self,data):
        r = requests.post(f"{self.base_url}/v12/presence", json=data)
        return r.json()
