# Real Integration Layer

## Meta
Subir de 5 a 8.5–9.

## Qué falta
No basta con datasets mock.
Hay que integrar con sistemas reales.

## Capas
### Source systems
- core banking
- fraud engines
- ERP / SAP-like
- SCADA / historian
- TMS / WMS
- CRM / ticketing
- event buses

### Connector layer
- REST adapters
- batch adapters
- SQL view adapters
- ERP export adapters
- telemetry adapters
- event-stream adapters

### Canonical validation
Todo debe mapear a:
- nodes
- edges
- events
- states
- labels
- external_fields

### Operational onboarding
- tenant
- credentials
- sample ingestion
- quality checks
- baseline
- alert route validation
