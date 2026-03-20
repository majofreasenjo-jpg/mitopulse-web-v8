# MitoPulse Stripe-level Global Architecture

## Goal
Deliver a global, enterprise-grade verification network that works even when users have:
- no wearable,
- basic phones,
- gaps in usage (hibernation),
- device swaps / loss / theft,
while preserving privacy (no raw biometrics stored server-side) and remaining auditable, scalable, and compliant.

## System overview
### Planes
- **Data plane**: edge packets → verify → state update → graph signals → decision output.
- **Control plane**: tenant onboarding, policy management, key management, quotas, observability, incident response.

### Key entities
- **Tenant**: enterprise customer with policy + key material.
- **Node**: (user_id, device_id, epoch) — “living identity instance”.
- **Packet**: signed proof bundle with derived features only (non-reversible).
- **Edge**: relationship between nodes (continuity, cohabitation/group, risk).

## Layered architecture (Capa 0–3)

### Capa 0 — Edge Node (User)
Runs on phone/watch/PC (or a basic phone tier).
Responsibilities:
- Signal ingestion (sensors or interaction features)
- Tiering (Tier0–Tier3)
- Sliding temporal vector (window)
- **Dynamic ID** and **packet hash**
- Risk / coercion / stability / human_conf heuristics
- **Signs the packet** (Ed25519) with a device private key stored in Secure Enclave/Keystore/TPM when available.

Output: **Proof Packet** (derived only)

### Capa 1 — Global Verify API (Gateway)
Entry point (Stripe-like API posture):
- TLS + mTLS for enterprise integrations
- Rate limit, WAF, bot protection
- Signature validation (raw-body, bit-perfect)
- Anti-replay (nonce + timestamp windows)
- Tenant policy lookup (tenant_id)
- Idempotency-Key enforcement

Output: ok/suspicious/fail + minimal explanation code

### Capa 2 — Identity State Store
Stores derived state only:
- rolling baselines (robust mean/std, EWMA, MAD)
- stability bands (per tier)
- device migration history (ICP edges)
- audit pointers (ledger hashes)
- per-tenant policy evaluation snapshots

No raw biometrics.

### Capa 3 — Trust Graph (Living system)
Graph computed from *derived behavioral meta-signals*:
- stability signatures
- drift trajectories
- coercion events
- device migration events
- context fingerprints (approx env tier/latency/hour-bucket)

Produces:
- clusters (work/unit/context/attack)
- quorum decisions (group verify)
- systemic anomaly alerts (cluster contagion)

## Services (recommended boundaries)

### Public edge-facing
1. **api-gateway**
2. **verify-service**

### Core
3. **state-service**
4. **trust-graph-service**
5. **policy-service**
6. **audit-ledger**

### Admin / control plane
7. **tenant-admin**
8. **key-service** (KMS/HSM)

### Infra / platform
9. **event-bus** (Kafka/NATS)
10. **observability** (OTel/Prom/Grafana/Loki)

## Multi-region strategy (Stripe-level)
- Active/active verify + read paths.
- Regional state with async replication; deterministic idempotency prevents double-apply.
- Audit ledger: region-local append + global consolidation (Merkle roots).
- Traffic steering: Geo DNS / Anycast + health-based routing.
- Backpressure: queue buffering + circuit breakers.

## Identity Continuity Protocol (ICP)
Handoff token path + lost-device recovery via enterprise admin or group quorum.

## Tier degradation
Tier0–Tier3; never drops to zero, only degrades confidence envelope.

## Diagrams
- `diagrams/system.mmd`
- `diagrams/dataflow.mmd`
- `diagrams/controlplane.mmd`
