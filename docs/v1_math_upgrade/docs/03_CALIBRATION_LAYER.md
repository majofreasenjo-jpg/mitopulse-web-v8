# Calibration Layer

## Objetivo
Que SCR, GSI y demás scores se interpreten como probabilidades útiles.

## Problema actual
Un score alto puede ser bueno para ranking, pero no necesariamente está calibrado.
Ejemplo:
- score 0.8 no siempre significa 80% de ocurrencia real

## Solución
Separar:
1. scoring
2. calibration

## Pipeline propuesto
raw score
-> calibration dataset
-> calibrator
-> calibrated probability

## Métodos candidatos
- isotonic calibration
- Platt / sigmoid calibration
- beta calibration (si se requiere más flexibilidad)

## Aplicación dentro de MitoPulse
- SCR_calibrated
- GSI_calibrated
- sector_risk_calibrated

## Outputs
- calibrated_probability
- calibration_error
- reliability_bucket
- decision_confidence_base

## Métricas
- Brier score
- Log loss
- Expected Calibration Error (ECE)
- reliability curve drift
