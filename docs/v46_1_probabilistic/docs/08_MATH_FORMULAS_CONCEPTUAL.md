# Fórmulas Conceptuales

## 1. Hierarchical Risk
HRM = w_n * R_node + w_c * R_cluster + w_e * R_ecosystem + w_f * R_field

## 2. Calibrated Probability
p_cal = Calibrator(HRM, domain)

## 3. Uncertainty band
[p_low, p_high] = UQ(p_cal, data_quality, drift, regime_uncertainty)

## 4. Hazard / Event Horizon
h_t = Hazard(p_cal, pressure_accumulation, criticality, reserve_stress)

## 5. Time-to-criticality
TTC = argmin_t { forecasted_risk(t) >= critical_threshold }

## 6. Forecast horizon
Forecast(t + k) = TGFE(graph_t, history, field_summaries, memory_state)

## Nota
Estas son fórmulas de arquitectura conceptual.
La implementación concreta puede variar por dominio y etapa.
