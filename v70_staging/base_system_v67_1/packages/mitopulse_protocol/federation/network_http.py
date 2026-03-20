import requests

class FederationNetworkHTTP:
    def __init__(self, nodes=None):
        self.nodes = nodes or []

    def broadcast(self, payload):
        responses = []
        for n in self.nodes:
            try:
                r = requests.post(f"{n}/protocol/evaluate", json=payload, timeout=2)
                responses.append({"node": n, "status": r.status_code, "ok": True})
            except Exception as e:
                responses.append({"node": n, "status": "fail", "ok": False, "error": str(e)})
        return responses
