# MitoPulse CloudScale Platform v3 (Production Scaffold)

Esta versión v3 transforma la arquitectura en un **scaffold productivo** listo para evolucionar hacia una infraestructura tipo:

- Stripe
- Cloudflare
- Auth0

## Novedades v3

- Event-driven architecture
- NATS event bus
- Postgres persistence
- Redis cache
- Auth Service (API keys / tenant tokens)
- Event workers
- OpenTelemetry observability
- Kubernetes deployment templates
- Billing metering
- Identity recovery service

## Arranque local

```bash
cd infra/docker
docker compose up --build
```

## Servicios

gateway : 8080  
identity_engine : 8081  
trust_graph : 8082  
continuity_service : 8083  
policy_engine : 8084  
dashboard : 8085  
audit_ledger : 8086  
recovery_service : 8087  
billing_meter : 8088  
auth_service : 8089  
event_worker : background
