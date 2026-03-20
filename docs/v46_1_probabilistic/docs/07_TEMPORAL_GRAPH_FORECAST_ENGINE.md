# Temporal Graph Forecast Engine (TGFE)

## Objetivo
Modelar cómo evoluciona el grafo en el tiempo.

## Componentes
- node memory
- edge persistence / drift
- propagation horizon
- forecasted cluster evolution
- forecasted GSI / SCR

## Horizontes
- short
- medium
- long

## Outputs
- forecasted_GSI
- forecasted_SCR
- node_risk_trajectory
- propagation_path_forecast
- expected_regime_by_horizon

## Regla de performance
Fast path:
- short horizon summary forecast

Deep path:
- medium / long replay and simulation
