# Performance Strategy

## Fast path (real time)
- RFDC
- HRM summary
- CE
- SUE lightweight
- EHE short window
- TGFE short horizon summary

## Deep path (on demand)
- full temporal graph replay
- medium / long horizon
- scenario analysis
- regime transition exploration

## Guardrails
- calibration refreshed periodically, not every event
- uncertainty uses lightweight summary features in real time
- temporal graph deep mode only in simulation / playback / crisis mode
