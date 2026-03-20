
# MitoPulse v2.5 — Architecture Blueprint

This blueprint extends the existing Universal v1 stack while keeping backward compatibility.

## Goals (v2.5)
- Preserve: tiers, risk scoring, coercion detection, HMAC dynamic_id, anti‑replay, audit logs, dashboard, PWA client.
- Add:
  - **Baseline profile** per user/device (rolling, derived).
  - **Stability score** (distance to baseline).
  - **Human confidence** (liveness heuristics; coherence + variability).
  - New read APIs:
    - `GET /v2/identity/state`
    - `GET /v2/identity/human-proof`

---

## System Overview

```mermaid
flowchart LR
  subgraph Client
    PWA[PWA Web App\n(Vite + React)]
    Phone[Mobile App (future)\nAndroid/iOS]
    Watch[Wearable (future)\nGalaxy Watch / Apple Watch]
  end

  subgraph EdgeLocal
    Engine[Physiology Engine\n(Index + Tier + Risk)]
    Baseline[Baseline Builder\n(rolling profile)]
    Human[Human Confidence\n(liveness heuristics)]
    Crypto[Crypto\n(HMAC dynamic_id + signature)]
  end

  subgraph Server
    API[FastAPI Backend]
    DB[(SQLite/Postgres)]
    Dash[Enterprise Dashboard\n(Jinja2)]
    Audit[Audit Logs]
  end

  PWA --> Engine
  Phone --> Engine
  Watch --> Phone

  Engine --> Baseline
  Baseline --> Human
  Human --> Crypto

  PWA -->|POST /v1/identity-events| API
  Phone -->|POST /v1/identity-events| API

  API --> DB
  API --> Dash
  API --> Audit

  PWA -->|GET /v2/identity/state| API
  PWA -->|GET /v2/identity/human-proof| API
```

---

## Data Model (v2.5)

### Identity Event (write path)
Minimum fields:
- `user_id`, `device_id`, `ts`, `request_id`
- `tier`, `index`, `risk`, `coercion`, `dynamic_id`
- optional signals/env

**NEW derived (server/pilot):**
- `baseline_index`, `baseline_std`
- `stability` (0..1)
- `human_confidence` (0..1)

---

## Formulas (v2.5)

### Stability score
```
z = abs(index - baseline_index) / max(baseline_std, 0.05)
stability = clamp01(exp(-z))
```

### Human confidence
Heuristic ∈ [0,1] using:
- impossible-combo penalties
- variability reward vs last event
- coherence reward (HR vs load, HRV vs stress)

---

## APIs
Existing:
- `POST /v1/identity-events`
- `POST /v1/verify`
- `GET /dashboard`

New:
- `GET /v2/identity/state?user_id=...&device_id=...`
- `GET /v2/identity/human-proof?user_id=...&device_id=...`

---

## Runbook
Backend:
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Web:
```bash
cd webapp
npm install
npm run dev -- --host 0.0.0.0 --port 5176
```

Simulator:
```bash
python sdk_shared/demo_simulator_v25.py --backend http://127.0.0.1:8000
```
