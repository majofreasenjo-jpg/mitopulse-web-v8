# MitoPulse v4 — Global Human Network

Scaffold de la red global de identidad humana para MitoPulse.

## Qué es
Una arquitectura de alcance planetario orientada a:
- verificación de presencia humana
- trust graph distribuido
- continuidad de identidad multi-dispositivo
- ledger criptográfico
- developer API universal
- operación multi-región

## Incluye
- microservicios desacoplados
- event bus
- Postgres / Redis / NATS
- region router
- ledger service
- developer portal API
- plantillas Kubernetes
- observabilidad base
- SDK Python

## Arranque local
```bash
cd infra/docker
docker compose up --build
```

## Puertos principales
- gateway: 8080
- dashboard: 8085
- developer_portal: 8090
- region_router: 8091
- ledger_service: 8092
