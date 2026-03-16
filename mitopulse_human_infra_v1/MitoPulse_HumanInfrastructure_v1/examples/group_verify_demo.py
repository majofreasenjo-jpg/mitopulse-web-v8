
import requests
BASE = "http://127.0.0.1:8000"
print(requests.post(BASE + "/v1/verify/group", json={
    "tenant_id": "demo",
    "members": [{"user_id":"manuel","device_id":"note9"}, {"user_id":"sofia","device_id":"iphone14"}],
    "require_quorum": 2,
    "min_stability": 0.55,
    "max_risk": 60
}).json())
