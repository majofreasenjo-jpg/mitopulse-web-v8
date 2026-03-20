
from edge_sdk_path import add_sdk_path
add_sdk_path()
import requests
from edge_sdk.client import MitoPulseEdgeClient

BASE = "http://127.0.0.1:8000"
tenant = "demo"
old = MitoPulseEdgeClient(BASE, tenant, "manuel", "note9")
new = MitoPulseEdgeClient(BASE, tenant, "manuel", "watch_r800")
print(old.register())
print(new.register())
tok = requests.post(BASE + "/v1/identity/continuity/start", json={"tenant_id": tenant, "user_id": "manuel", "old_device_id": "note9", "new_device_id": "watch_r800"}).json()["token"]
print(requests.post(BASE + "/v1/identity/continuity/complete", json={"tenant_id": tenant, "user_id": "manuel", "old_device_id": "note9", "new_device_id": "watch_r800", "token": tok}).json())
