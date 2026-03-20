# MitoPulse Production Architecture v3

Clients / SDKs
      ↓
Global Gateway
      ↓
Auth Service
      ↓
Event Bus (NATS)
 ├ Identity Engine
 ├ Trust Graph
 ├ Continuity Service
 ├ Recovery Service
 ├ Policy Engine
 ├ Billing Meter
 ├ Audit Ledger
 └ Event Workers

State Stores
- Postgres
- Redis

Observability
- OpenTelemetry
- Grafana
- Prometheus
