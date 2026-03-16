# MitoPulse — Stripe-level Architecture (Reference Package)

This package is a **production-grade architecture blueprint** for a global, multi-tenant identity verification network:
**Edge proof packets → Global Verify API → Identity State Store → Trust Graph → Policy & Quorum decisions**, with
audit-grade observability, idempotency, and multi-region resilience.

## What you get
- Architecture docs (service boundaries, data flows, threat model, SLAs).
- Mermaid diagrams for system + data-plane/control-plane.
- Local developer stack (Docker Compose) to **boot a realistic topology** (API gateway + queue + postgres + redis + observability).
- Kubernetes + Terraform placeholders (opinionated structure, ready to fill).

## Quickstart (local topology)
Prereqs: Docker Desktop.

```bash
cd infra/docker
docker compose up -d
```

Then open:
- Grafana: http://localhost:3000  (admin/admin)
- Prometheus: http://localhost:9090
- API Gateway (placeholder): http://localhost:8080

> Note: This package is an **architecture deliverable**: service folders include stubs and contracts
(OpenAPI, message schemas). You can plug your current MitoPulse code into these boundaries.

See `docs/architecture.md` for the full blueprint.
