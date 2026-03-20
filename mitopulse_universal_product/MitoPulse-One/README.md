# MitoPulse One — Universal Pilot (PWA + Enterprise API/Dashboard)

Universal = runs on **PC/Notebook** and works on **any mobile/tablet** via browser (PWA).  
This is the **shareable off-store pilot**: run it once, then anyone can open the PWA and demo.

## Stack
- Backend: FastAPI (API + Enterprise Dashboard)
- Web App: Vite + React (PWA-style demo UI)
- SDK: Python simulator
- Docker Compose included

## Quick Start (Local)
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
- Dashboard: http://127.0.0.1:8000/dashboard
- API Docs: http://127.0.0.1:8000/docs

### Web App (PWA)
```bash
cd webapp
npm install
npm run dev -- --host 0.0.0.0 --port 5176
```
- PWA: http://127.0.0.1:5176

## Quick Start (Docker)
```bash
docker compose up --build
```

## Simulator
```bash
cd sdk
python -m venv .venv
# activate...
pip install -r requirements.txt
python simulator.py --backend http://127.0.0.1:8000 --live
```

## Global demo links (optional)
See `infra/cloudflare/README.md`.
