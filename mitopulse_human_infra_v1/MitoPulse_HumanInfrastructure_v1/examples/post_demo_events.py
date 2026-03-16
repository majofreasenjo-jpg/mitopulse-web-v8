
from edge_sdk_path import add_sdk_path
add_sdk_path()
from edge_sdk.client import MitoPulseEdgeClient

BASE = "http://127.0.0.1:8000"
tenant = "demo"
manuel = MitoPulseEdgeClient(BASE, tenant, "manuel", "note9")
sofia = MitoPulseEdgeClient(BASE, tenant, "sofia", "iphone14")

print(manuel.register())
print(sofia.register())
print(manuel.send_presence("tier1", 0.61, 0.72, 0.86, 35, False, {"cluster":"work"}))
print(sofia.send_presence("tier2", 0.67, 0.79, 0.90, 20, False, {"cluster":"work"}))
print(manuel.send_presence("tier1", 0.22, 0.18, 0.84, 95, True, {"cluster":"attack"}))
