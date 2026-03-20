# MitoPulse CloudScale Platform v2

Versión v2 del scaffold de plataforma global de MitoPulse.

## Novedades
- Postgres y Redis en la topología
- NATS event bus
- Recovery Service
- Billing / Usage Metering
- Gateway con tenancy e idempotency
- Observabilidad base

## Arranque
```bash
cd infra
docker compose up --build
```

Puertos:
- gateway 8080
- identity_engine 8081
- trust_graph 8082
- continuity_service 8083
- policy_engine 8084
- dashboard 8085
- audit_ledger 8086
- recovery_service 8087
- billing_meter 8088
- postgres 5432
- redis 6379
- nats 4222
