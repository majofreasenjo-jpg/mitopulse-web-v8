# Detection + Collapse Engines

Esta versión agrega dos motores ejecutables desde la web:

## 1. Fraud & Anomaly Detection Engine v1
Detecta:
- velocity anomalies
- shadow coordination
- high signal pressure

Endpoint:
- `/api/detection/run`

## 2. Systemic Collapse Predictor v1
Calcula:
- NHI
- TPI
- SCR
- entropy
- criticality
- climate pressure
- vortex score

Endpoint:
- `/api/systemic/run`

## Uso desde el dashboard
En `Detection Studio`:
- `Run Fraud Detection`
- `Run Collapse Predictor`

## Dataset usado
Busca automáticamente en:
- `live_output/yahoo_live_market`
- `live_output/binance_live_crypto`
- `data/afp_systemic_realistic_v1`
- `data/bank_medium_realistic_v1`
