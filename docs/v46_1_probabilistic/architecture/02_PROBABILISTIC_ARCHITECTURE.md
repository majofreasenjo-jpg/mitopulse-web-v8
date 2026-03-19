# Arquitectura Probabilística v46.1

## Núcleo preservado
- RFDC
- GSI / NHI / TPI / SCR / CPI / ASI / CDI / RRI
- Decision Engine
- Action Engine
- MitoPulse Verify

## Nueva capa probabilística

### A. Hierarchical Risk Model (HRM)
Combina riesgo por:
- nodo
- cluster
- ecosistema
- campo externo

### B. Calibration Engine (CE)
Transforma score bruto en probabilidad calibrada.

### C. Structured Uncertainty Engine (SUE)
Transforma probabilidad puntual en:
- banda inferior
- banda superior
- confidence grade
- tipo de incertidumbre

### D. Event-Horizon / Hazard Engine (EHE)
Estima:
- probabilidad de transición a estado crítico
- tiempo esperado a criticalidad
- ventana temporal de riesgo

### E. Temporal Graph Forecast Engine (TGFE)
Estima:
- GSI futuro
- SCR futuro
- trayectorias de nodos / clusters
- rutas probables de propagación

## Flujo
Signals / states / fields
-> RFDC
-> raw systemic features
-> HRM
-> CE
-> SUE
-> EHE
-> TGFE
-> dashboard / Verify / actions
