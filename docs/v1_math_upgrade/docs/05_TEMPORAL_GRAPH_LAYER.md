# Temporal Graph Layer

## Objetivo
Modelar cómo cambia el sistema en el tiempo, no solo cómo está ahora.

## Qué añade
- memory by node
- edge evolution
- trajectory forecasting
- propagation horizon
- event-time sensitivity

## Horizontes sugeridos
- short horizon
- medium horizon
- long horizon

## Outputs
- forecasted_GSI
- forecasted_SCR
- propagation_path_forecast
- regime_change_horizon
- node_risk_trajectory

## Integración
Current graph snapshot
+ historical graph deltas
+ external field summaries
-> temporal graph engine
-> horizon forecasts

## Regla de performance
- fast path: snapshot + short horizon
- deep path: playback + temporal simulation
