# MitoPulse v46.2 — Live Graph Forecast + WaveEngine + DemoKiller

Este paquete agrega al stack v46.1:
- módulo exacto de grafo vivo
- forecast corto integrado
- WaveEngine + TGFE-like short horizon
- Invisible Storm mejorado
- dashboard en tiempo real (demo operativa local)

## Qué muestra
- nodos vivos
- ondas propagándose
- forecast de riesgo por horizonte corto
- trigger zones
- pressure field
- playback del DemoKiller mejorado

## Cómo correr
1. `pip install -r requirements.txt`
2. `uvicorn backend.main:app --reload`
3. abrir `http://127.0.0.1:8000`
