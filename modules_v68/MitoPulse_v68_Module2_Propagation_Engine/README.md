# MitoPulse v68 — Module 2 Propagation Engine

Motor real de propagación multi-asset para MitoPulse.

## Qué incluye
- Conector público a Binance Spot
- Descarga de klines para múltiples activos
- Construcción de series de retornos
- Matriz de correlación dinámica
- Estimación simple de delays por lag
- Grafo ponderado de propagación
- Propagation engine con shock injection
- Script de demo

## Activos por defecto
BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT, ADAUSDT, AVAXUSDT, DOGEUSDT, MATICUSDT, TONUSDT

## Instalación
pip install -r requirements.txt

## Demo
python scripts/run_propagation_demo.py
