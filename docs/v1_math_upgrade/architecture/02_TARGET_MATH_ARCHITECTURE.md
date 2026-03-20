# Arquitectura Matemática Objetivo

## Core
- RFDC
- GSI / NHI / TPI / SCR / CPI / ASI / CDI / RRI

## Nueva envoltura matemática

### A. Calibration Layer
Convierte score -> probabilidad calibrada

### B. Uncertainty Layer
Convierte probabilidad puntual -> banda / intervalo / confianza

### C. Temporal Graph Layer
Convierte estado instantáneo -> trayectoria futura del grafo

### D. Benchmark Layer
Convierte percepción de calidad -> evidencia cuantitativa reproducible

## Flujo
Signals -> RFDC -> raw scores -> Calibration Layer -> calibrated probabilities
-> Uncertainty Layer -> decision confidence
-> Temporal Graph Layer -> horizon forecasts
-> Benchmark Layer -> validation / monitoring
