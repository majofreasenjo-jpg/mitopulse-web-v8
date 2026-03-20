import requests

class MitoPulsePlanetaryClient:

    def __init__(self,base_url):
        self.base_url=base_url

    def presence(self,data):

        r=requests.post(f"{self.base_url}/v6/presence",json=data)

        return r.json()
