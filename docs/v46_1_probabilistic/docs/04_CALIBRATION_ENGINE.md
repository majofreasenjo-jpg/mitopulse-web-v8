# Calibration Engine (CE)

## Objetivo
Que una probabilidad emitida por MitoPulse sea interpretable como probabilidad real.

## Entrada
- hierarchical_risk_score
- raw SCR
- raw GSI
- raw sector indices

## Salida
- calibrated_probability
- calibration_error
- reliability_bucket

## Métodos
- isotonic regression
- sigmoid / Platt-like calibration
- beta calibration (opcional avanzado)

## Reglas
- calibración por dominio
- calibración por tenant grande cuando haya datos
- monitoreo de drift de calibración

## Métricas
- Brier score
- Log loss
- ECE
- reliability curves
