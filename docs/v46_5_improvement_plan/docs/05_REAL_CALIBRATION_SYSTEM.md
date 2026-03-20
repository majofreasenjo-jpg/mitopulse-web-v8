# Real Calibration System

## Meta
Subir de 4 a 9+.

## Problema actual
La calibración conceptual o sintética no basta.

## Solución
### A. Calibration Dataset Engine
Construir datasets con:
- raw score
- contextual features
- real outcome
- domain
- timestamp window
- tenant / cohort

### B. Domain calibrators
Un calibrador por:
- banking
- marketplace
- energy
- logistics

### C. Recalibration policy
- periodic refresh
- minimum sample thresholds
- drift-triggered recalibration

### D. Drift monitor
- ECE drift
- Brier drift
- domain calibration decay

## Métricas obligatorias
- Brier Score
- Log Loss
- ECE
- reliability curves
- calibration by bucket
