# Connector Blueprints

## Adapter contract
Todo conector debe exponer:
- connector_name
- source_type
- polling_or_streaming
- schema_mapping
- canonical_output

## Ejemplo de blueprint
- RESTAdapter
- BatchCSVAdapter
- SQLViewAdapter
- OPCUAAdapter
- MQTTAdapter
- TelemetryAdapter
- ERPExportAdapter
- EventBusAdapter

## Salida estándar
Todos los adaptadores deben entregar:
- nodes
- edges
- events
- states
- labels
- external_fields
