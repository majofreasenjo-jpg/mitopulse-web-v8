# Temporal Forecast Upgrade

## Meta
Subir de 6.5 a 8.5–9.

## Mejoras
### 1. Short horizon real-time
- current to near-future propagation
- critical window probability
- time-to-criticality

### 2. Medium horizon
- likely path evolution
- cluster stress trajectory
- external field interaction

### 3. Long horizon
- scenario replay
- regime transition maps
- collapse basin exploration

## Nuevos outputs
- forecasted_GSI_short
- forecasted_SCR_short
- propagation_path_likelihood
- regime_change_horizon
- node_risk_trajectory
- expected_time_to_criticality

## Regla de performance
- fast path: short horizon only
- deep path: medium/long on demand
