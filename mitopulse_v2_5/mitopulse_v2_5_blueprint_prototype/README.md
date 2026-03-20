
# MitoPulse v2.5 — Blueprint + Prototype

Includes:
- `docs/`  → Architecture Blueprint
- `backend/` → FastAPI backend + dashboard + v2.5 read APIs
- `sdk_shared/` → engine + simulator
- `webapp/` → React/Vite pilot PWA

## Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Open:
- http://127.0.0.1:8000/dashboard
- http://127.0.0.1:8000/docs

## Simulator
```bash
cd sdk_shared
pip install requests
python demo_simulator_v25.py --backend http://127.0.0.1:8000
```

## Web App
```bash
cd webapp
npm install
npm run dev
```

Open:
- http://127.0.0.1:5176

## v2.5 APIs
- `GET /v2/identity/state?user_id=...&device_id=...`
- `GET /v2/identity/human-proof?user_id=...&device_id=...`

## Optional security
- `MITOPULSE_API_KEY=...` (send `X-API-Key`)
- `MITOPULSE_REQUIRE_SIG=1`
- `MITOPULSE_DEMO_DEVICE_SECRET=demo-super-secret-device-key`
