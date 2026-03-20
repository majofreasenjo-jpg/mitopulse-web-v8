# MitoPulse v43.3 Live Real

Versión local + deploy con:
- dashboard web multi-tab
- IA conectada de forma modular
- live connectors ampliados
- acciones reales en sandbox
- tabs separados para no saturar el sistema
- modo marketplace / bank / energy / full

## Incluye
- Executive View
- Graph Live
- System Dynamics
- System Brain
- Memory & Behavior
- AI Layer
- Simulation / Demo Killers
- Alerts & Actions
- Vertical Mode

## Live connectors incluidos
- Yahoo Finance
- Binance
- FRED / macro
- Alpha Vantage
- CoinGecko
- EIA (energía)
- NOAA (weather / climate)
- MarineTraffic-like mock (logística marítima)

## Local
1. Copia `.env.example` a `.env`
2. `pip install -r requirements.txt`
3. `uvicorn backend.main:app --reload`
4. abre `http://127.0.0.1:8000`

## Render
1. sube esta carpeta a GitHub
2. conecta el repo en Render
3. Render detecta `render.yaml`
4. agrega tus variables `.env` como Environment Variables

## Importante
La IA no reemplaza el núcleo RFDC. La IA:
- limpia / normaliza
- clasifica anomalías
- genera mutaciones
- explica resultados
- sugiere estrategias
