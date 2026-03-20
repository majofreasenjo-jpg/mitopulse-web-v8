# Uncertainty Layer

## Objetivo
No entregar solo un número, sino rango y confianza.

## Qué añade
- prediction intervals
- confidence bands
- optimistic / base / pessimistic views
- aleatoric vs systemic uncertainty hints

## Outputs recomendados
- p_event
- p_low
- p_high
- uncertainty_bandwidth
- confidence_grade

## Uso práctico
Ejemplo:
SCR_calibrated = 0.74
interval = [0.61, 0.83]

Interpretación:
- riesgo alto
- con incertidumbre moderada
- acción sugerida: verify / review_and_limit

## Beneficios
- reduce sobreconfianza
- mejora explainability
- mejora decisiones humanas
