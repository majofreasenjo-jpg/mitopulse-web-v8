# MitoPulse v2 (TrustGraph + ICP) — OFF-STORE PILOT

This package upgrades v1 to **Ed25519 signed proof packets**, **Group Quorum Verification**, and an **Identity Continuity Protocol (ICP)**.

## What you get
- Backend (FastAPI + SQLite + Enterprise Dashboard)
- Gateway Verify APIs (anti-replay, signature verification)
- Derived Identity State Store (no raw biometrics)
- Trust Graph edges (continuity / cohab / risk)
- ICP migration endpoints (handoff + complete)
- Edge Node simulator (Tier0 fallback supported)

## Run backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open dashboard: http://127.0.0.1:8000/dashboard

## Run edge scenarios
```bash
cd edge_node
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/register_device.py --device note9 --user manuel
python scripts/run_scenarios.py --device note9 --user manuel
```

## Group quorum demo
```bash
python scripts/group_verify_demo.py
```

## ICP migration demo (device change)
```bash
python scripts/icp_migration_demo.py --old note9 --new watch_r800
```

## Notes
- Tier0 supports basic phones/no wearable using interaction proxies (tap_rate, keystroke_var).
- Anti-replay is enforced via UNIQUE request_id in SQLite.
