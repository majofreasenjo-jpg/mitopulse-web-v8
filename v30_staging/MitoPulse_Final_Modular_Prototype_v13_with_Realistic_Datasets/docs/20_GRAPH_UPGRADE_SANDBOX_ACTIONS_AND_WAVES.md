# Graph Upgrade + Sandbox Actions + Wave Engine Visual

Esta versión agrega tres cierres clave:

## 1. Mejor visual del grafo
- posiciones más legibles
- enlaces inferidos más claros
- layout estilo spring/radial
- nodos de alerta/guardian/hidden diferenciados

## 2. Acción real en sandbox
Nuevo endpoint:
- `/api/action/sandbox/<entity_id>/<action>`
- `/api/action/sandbox/state`

Permite simular acciones reales como:
- monitor
- enhanced_monitoring
- review_and_limit
- block_or_freeze

Persistencia:
- `sandbox/sandbox_state.json`

## 3. Wave Engine visual on the move
- anillos de onda animados sobre el grafo RFDC
- playback con grafo que evoluciona paso a paso
- visualización de action threshold
