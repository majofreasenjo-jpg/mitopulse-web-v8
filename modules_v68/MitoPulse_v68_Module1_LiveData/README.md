# MitoPulse v68 — Module 1 Live Data

Módulo real y utilizable para ingestión de datos de mercado desde Binance Spot
con fallback opcional a CoinGecko y normalización hacia un payload compatible
con el protocolo MitoPulse.

## Qué incluye
- Conector público real a Binance Spot
- Fallback opcional a CoinGecko
- Normalización a payload protocolar
- Script de prueba manual
- Tests con mocks
- Soporte para múltiples activos top mercado

## Activos por defecto
BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT, ADAUSDT, AVAXUSDT, DOGEUSDT, MATICUSDT, TONUSDT

## Instalación
pip install -r requirements.txt

## Prueba rápida
python scripts/run_live_snapshot.py

## Nota
Este módulo no requiere API key para endpoints públicos de Binance Spot.
