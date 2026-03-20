# MitoPulse v2 — DEMO GLOBAL (Off-store)

Goal: share an installable app-like experience with partners, without app stores, and without localhost.

## Architecture
- Backend: FastAPI + SQLite + Enterprise dashboard + audit logs
- Client: PWA (Vite + React) that computes index locally and posts derived events to backend
- Optional simulator: posts sample events from a PC

---

## 1) Local run (dev)
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Webapp
```bash
cd webapp
npm install
npm run dev
```

Open:
- PWA: http://localhost:5176
- Backend docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/dashboard

---

## 2) Share globally (no servers yet): Tunnel
Use this when you want the *fastest* way to demo to partners.

### ngrok (fast)
```bash
ngrok http 8000
```
Copy the HTTPS URL and paste it into the PWA “Backend URL”.

### Cloudflare Tunnel (recommended free)
```bash
cloudflared tunnel --url http://localhost:8000
```

---

## 3) Real global demo (recommended): Deploy backend to a small VPS
Any VPS works. Recommended: Ubuntu 22.04.

### Option A — Docker (easiest)
Create an `nginx` reverse proxy and run uvicorn behind it (TLS). See `infra/` notes (you can add later).

### Option B — Uvicorn systemd (simple)
- Install python3, create venv, run uvicorn on 0.0.0.0:8000
- Open firewall 8000
- Put behind Cloudflare / Nginx for HTTPS

---

## 4) Make it “installable”
- Android/Chrome: menu → “Add to Home screen”
- iOS/Safari: Share → “Add to Home Screen”

---

## 5) Build the PWA and host it
When you want a single URL for everything:
1. Deploy backend (HTTPS)
2. Build the webapp:
```bash
cd webapp
npm run build
```
3. Copy `webapp/dist` to `backend/app/static/pwa/` and redeploy backend.
Then the app is available at:
- https://YOUR_DOMAIN/pwa
