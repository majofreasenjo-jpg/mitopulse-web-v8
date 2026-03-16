
# MitoPulse v17 – Guardian Node Layer

Esta versión introduce **Guardian Nodes** dentro del grafo.

## Qué hacen
- monitorean rutas críticas
- reciben propagación de riesgo
- aplican políticas sectoriales
- pueden decidir:
  - ALLOW
  - REVIEW
  - BLOCK

## Ejemplos de guardianes
- guardian_bank_01
- guardian_telco_01

## Ejecutar
pip install fastapi uvicorn
uvicorn app.main:app --reload

## Probar
Abrir:
http://127.0.0.1:8000/docs
