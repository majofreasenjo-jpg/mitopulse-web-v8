# Data Model & Contracts

## Canonical packet format (v4)
Signed over raw body bytes.

Fields: tenant_id, user_id, device_id, epoch, ts, nonce, tier, idx, stability, human, risk, coercion, features, packet_hash, signature.

## Topics
packets.ingested, state.updated, graph.edges.inferred, graph.clusters.snapshot, policy.decisions, audit.ledger.append
