import requests, time

BASE = "http://127.0.0.1:8000"

print("=== MitoPulse Full Rebuild Package - Quick Test ===\n")

# Health check
r = requests.get(f"{BASE}/health", timeout=5)
print(f"Health: {r.json()}\n")

# Post 3 events
scenarios = [
    {"user": "demo_user", "device": "rebuild_pc", "ts": int(time.time()) - 86400, "dynamic_id": "abc123", "index": 0.72, "tier": "tier2", "risk": 0},
    {"user": "demo_user", "device": "rebuild_pc", "ts": int(time.time()) - 43200, "dynamic_id": "def456", "index": 0.45, "tier": "tier2", "risk": 25},
    {"user": "demo_user", "device": "rebuild_pc", "ts": int(time.time()), "dynamic_id": "ghi789", "index": 0.18, "tier": "tier1", "risk": 90},
]
for i, evt in enumerate(scenarios):
    r = requests.post(f"{BASE}/v1/identity-events", json=evt, timeout=5)
    print(f"Event {i+1}: idx={evt['index']}  tier={evt['tier']}  risk={evt['risk']}  -> {r.json()}")

# Dashboard (JSON)
print()
r = requests.get(f"{BASE}/dashboard", timeout=5)
dash = r.json()
print(f"Dashboard: {len(dash['events'])} events stored")
for e in dash["events"]:
    print(f"  user={e['user']}  idx={e['index']}  tier={e['tier']}  risk={e['risk']}")

print("\n=== Test Complete ===")
