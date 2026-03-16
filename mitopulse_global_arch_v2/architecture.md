
# Arquitectura Global

Capas principales:

CLIENTES
- PWA
- Apps móviles
- Wearables (fuente de señales)

EDGE
- CDN
- WAF
- TLS
- Rate limiting

CORE API
Endpoints:

GET /health
POST /identity/event
POST /identity/verify
GET /identity/state
GET /identity/human-proof

ENGINE
Procesamiento de señales:

HR
HRV
SpO2
Sleep Score
Load

Outputs:

stability
human_confidence
risk
coercion

STORAGE

Redis -> estado en tiempo real
Postgres -> histórico / auditoría

SURFACES

Enterprise Dashboard
Admin Console
Audit Logs
