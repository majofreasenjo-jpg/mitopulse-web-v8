
# MitoPulse Human Infrastructure v1

## Layer 1 — Human Presence Engine
- signal ingestion
- tier detection
- stability / human confidence / risk / coercion

## Layer 2 — Global Trust Graph
Nodes:
`(tenant_id, user_id, device_id, epoch)`

Edges:
- continuity
- cohab
- risk

## Layer 3 — Identity Continuity Network
- handoff tokens
- epoch migration
- trusted recovery

## Layer 4 — Universal Developer API
- POST /v1/devices/register
- POST /v1/presence/event
- GET /v1/identity/state
- GET /v1/identity/human-proof
- POST /v1/identity/continuity/start
- POST /v1/identity/continuity/complete
- POST /v1/identity/recovery/request
- POST /v1/identity/recovery/approve
- POST /v1/verify/group
- GET /v1/graph/edges
