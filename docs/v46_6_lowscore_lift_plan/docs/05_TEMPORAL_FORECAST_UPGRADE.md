# Temporal Forecast Upgrade

## Cambio principal
Se reemplaza forecast corto lineal por:
- short-horizon dynamic forecast
- propagation path likelihood
- expected time-to-criticality
- regime change horizon

## Nuevo output
- forecasted_GSI_short
- forecasted_SCR_short
- path_likelihood
- TTC (time to criticality)
- regime_horizon

## Mecánica
El forecast ahora depende de:
- memoria de nodos
- persistencia de aristas
- presión externa
- damping / amplification
- reserve stress
