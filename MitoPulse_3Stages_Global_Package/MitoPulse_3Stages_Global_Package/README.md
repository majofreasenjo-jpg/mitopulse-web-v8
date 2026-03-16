# MitoPulse — 3 Stages Global Package

## Etapa 1 — Product Demo
- Presence Engine
- Risk Engine
- Verify API
- SDK Python
- Dashboard
- PWA instalable

## Etapa 2 — Hardening Core
- gateway
- auth_service
- verify_api
- trust_graph
- ledger
- billing
- topología con Postgres / Redis / NATS

## Etapa 3 — Global Clients
- Web PWA
- Mobile Expo wrapper
- Wear OS scaffold
- watchOS scaffold
- Caddy
- Cloudflare Tunnel sample

## Ejecución inmediata
```bash
cd stage1_product_demo/infra
docker compose up --build
```

Luego:
- API: http://localhost:8000/docs
- Dashboard: http://localhost:8000/dashboard
- App instalable: http://localhost:8000/app
