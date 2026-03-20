# MitoPulse v68 — Module 6 Federation + Quorum

Módulo real para validación distribuida, quorum y lock-in protocolar.

## Qué incluye
- Modelo de voto de nodos
- Cálculo de quorum ponderado
- Registro de anchors / validators
- Simulación multi-node
- API básica para federación
- Broadcast y recolección de votos
- Trazabilidad de decisión federada

## Instalación
pip install -r requirements.txt

## Demo local
python scripts/run_federation_api.py

## Endpoints principales
- GET /health
- GET /validators
- POST /vote
- POST /quorum/evaluate
- POST /federation/broadcast_demo
