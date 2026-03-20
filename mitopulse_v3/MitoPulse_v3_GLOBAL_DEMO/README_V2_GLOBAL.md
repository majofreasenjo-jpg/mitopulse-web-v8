# MitoPulse v2 — DEMO GLOBAL (Universal Off-store)

This package lets you demo MitoPulse like a real app (installable PWA) without app stores.

## What you get
- Enterprise backend (FastAPI) with:
  - /v1/identity-events (derived-only)
  - /v1/verify (on-demand verification)
  - /dashboard (dark enterprise UI with risk/coercion badges)
  - /docs (Swagger)
  - audit logs
  - anti-replay for identity events via request_id UNIQUE
- PWA client (Vite + React) that:
  - computes tier/index locally
  - posts derived events to backend
  - verifies latest dynamic_id
  - opens dashboard/docs
- Optional PC simulator (Python) to generate 5-day demo data

## Quick start
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Webapp
```bash
cd webapp
npm install
npm run dev
```

Open:
- PWA: http://localhost:5176
- Dashboard: http://127.0.0.1:8000/dashboard

## Global demo (no localhost)
See DEPLOYMENT.md for ngrok / Cloudflare Tunnel / VPS.
