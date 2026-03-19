# Modelo Canónico MitoPulse

## Objetivo
Traducir cualquier sistema existente a un lenguaje universal para RFDC.

## Estructuras base

### Node
- node_id
- node_type
- tenant_id
- industry
- attributes
- status
- location
- criticality_hint

### Edge
- edge_id
- from_node
- to_node
- relation_type
- strength
- direction
- confidence

### Event
- event_id
- timestamp
- event_type
- source_node
- target_node
- metric_name
- metric_value
- severity
- source_system

### State
- state_id
- node_id
- state_type
- value
- valid_from
- valid_to

### Label
- label_id
- entity_id
- label_type
- value
- confidence
- origin

### External Field
- field_id
- field_type
- region
- intensity
- coupling_hint
- timestamp

## Regla
Todo conector debe poder mapear sus fuentes a estas estructuras.
