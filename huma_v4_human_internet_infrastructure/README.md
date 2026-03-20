# Huma v4 — Human Internet Infrastructure

Repositorio ejecutable independiente de la arquitectura v4.

## Qué incluye
- gateway
- edge_orchestrator
- presence_engine
- risk_engine
- continuity_engine
- device_trust_engine
- anti_spoof_engine
- fraud_memory
- graph_engine
- challenge_engine
- trust_engine
- policy_engine
- feature_flag_service
- identity_continuity_protocol
- reputation_network
- dashboard
- admin_panel
- sdk/web

## Arranque
```bash
cd infra
docker compose up --build
```

## URLs
- Gateway docs: http://localhost:8000/docs
- Dashboard: http://localhost:8010
- Admin panel: http://localhost:8013
- Feature flags: http://localhost:8011/docs
- Policy engine: http://localhost:8007/docs
- Reputation network: http://localhost:8014/health
- Identity continuity: http://localhost:8015/health
- Edge orchestrator: http://localhost:8016/health

## Endpoint principal
```http
POST /v4/verify-human
```
