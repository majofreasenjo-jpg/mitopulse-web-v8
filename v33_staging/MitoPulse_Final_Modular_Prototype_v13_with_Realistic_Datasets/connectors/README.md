# MitoPulse Live Connectors v1

Capa de ingestión viva para conectar MitoPulse con fuentes online y batch.

## Objetivo
Transformar feeds externos a un formato canónico que el prototipo ya entiende:

- customers.csv
- devices.csv
- events.csv
- signals.csv

## Conectores incluidos
- `rest_connector.py` → polling HTTP/REST
- `websocket_connector.py` → streaming WebSocket
- `file_drop_connector.py` → batch folder watcher
- `normalizer.py` → normalización al formato canónico
- `router.py` → orquestador simple
- `schemas/canonical_schema.json` → contrato de datos
- `configs/*.json` → ejemplos de configuración

## Flujo
Fuente externa → Connector → Normalizer → `/live_output/<source>/...csv` → Loader MitoPulse
