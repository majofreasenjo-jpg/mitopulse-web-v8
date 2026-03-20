# Security, Threat Model, and Controls

## Threat model
Replay, forgery, canonicalization drift, device theft, sybil clusters, insider access, tenant leakage.

## Stripe-level controls
- Validate signatures on **raw request body** (bit-perfect).
- Nonce + timestamp replay window.
- Idempotency on writes (Idempotency-Key + packet_hash).
- Derived-only storage; encrypt at rest with KMS.
- Immutable audit ledger (hash-chained).
- Per-tenant keys with rotation and audit trails.
