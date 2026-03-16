# System Architecture

```text
Clients / SDKs
   ↓
Edge / Gateway
   ↓
Policy Engine ───────────────┐
   ↓                         │
Identity Engine              │
   ↓                         │
Trust Graph ───────┐         │
   ↓               │         │
Continuity Service │         │
   ↓               │         │
Audit Ledger ◄─────┴─────────┘
   ↓
Dashboard / Admin / Developer API
```

## Stores recomendados (siguiente fase)
- Postgres: historial, tenants, policies
- Redis: state cache, replay protection
- Object storage: snapshots y exports
- Event bus: NATS / Kafka
