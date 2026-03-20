# MitoPulse CloudScale Platform v1

Este paquete es un **scaffold de plataforma de escala global** para evolucionar MitoPulse hacia una infraestructura tipo Stripe/Auth0/Cloudflare.
No pretende ser una implementación completa del tamaño de Stripe o Cloudflare hoy mismo; sí es una **base ejecutable, modular y lista para extender**.

## Incluye
- Monorepo de microservicios
- API Gateway
- Identity Engine
- Trust Graph Service
- Identity Continuity Service
- Policy Engine
- Audit Ledger
- Dashboard API
- Docker Compose
- OpenAPI base
- SDK Python mínimo
- Documentación de arquitectura, tenancy, seguridad y operación

## Arranque local
```bash
cd infra
docker compose up --build
```

Luego abre:
- Gateway: http://127.0.0.1:8080/docs
- Dashboard: http://127.0.0.1:8085/docs

## Servicios
- gateway: 8080
- identity_engine: 8081
- trust_graph: 8082
- continuity_service: 8083
- policy_engine: 8084
- dashboard: 8085
- audit_ledger: 8086
