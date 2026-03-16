# MitoPulse CloudScale Platform v2

Clients / SDKs
  ↓
Gateway (tenancy + idempotency)
  ↓
NATS Event Bus
  ├── Identity Engine
  ├── Trust Graph
  ├── Continuity Service
  ├── Recovery Service
  ├── Audit Ledger
  └── Billing Meter
  ↓
State Stores
  - Postgres
  - Redis
  ↓
Dashboard / Admin APIs
