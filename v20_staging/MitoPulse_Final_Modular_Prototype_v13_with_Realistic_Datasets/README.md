# MitoPulse Final Modular Prototype v13

Prototipo final modular completo de MitoPulse basado en la plataforma institucional v12, ampliado con la arquitectura total del baúl de seguridad.

## Incluye
- Dashboard institucional final con grafo vivo y colores oficiales
- Perfiles modulares por industria / tamaño / escenario
- Crisis históricas pre / mid / post crisis
- Demo Killer Studio:
  - The Invisible Storm
  - The Invisible Network
  - The Coming Collapse
- Runtime map visible
- Mathematical core visible
- Upload de datasets

## Cómo correr
```bash
cd MitoPulse_Final_Modular_Prototype_v13
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn api.app:app --reload
```

Abrir:
- http://127.0.0.1:8000/

## KPIs ejecutivos
- NHI
- TPI
- SCR

## Índice técnico estructural
- MDI



## Ejecutar en la web
### Local
```bash
pip install -r requirements.txt
bash start_web.sh
```

### Docker
```bash
docker build -t mitopulse-live .
docker run -p 8000:8000 mitopulse-live
```

### Render / Railway / hosts compatibles con Docker
- usar `Dockerfile`
- comando ya embebido en `start_web.sh`
- también se incluye `render.yaml`

## Live Connectors en web
Desde el dashboard puedes ejecutar:
- Yahoo Finance (REST)
- Binance (WebSocket)
- file drop batch

Cada connector genera salida canónica en:
- `live_output/<source>/customers.csv`
- `live_output/<source>/devices.csv`
- `live_output/<source>/events.csv`
- `live_output/<source>/signals.csv`



## Detección y predicción activadas
Esta versión agrega:
- `core/fraud_detection_engine.py`
- `core/systemic_collapse_predictor.py`

Endpoints:
- `/api/detection/run`
- `/api/systemic/run`

También quedan expuestos desde el dashboard, en `Detection Studio`.



## RFDC integrado
Esta versión agrega integración total del sistema vivo mediante:

- `core/rfdc.py`
- `/api/rfdc/run`
- `RFDC Studio` en el dashboard

RFDC une:
- Detection Engine
- Relational Dark Matter
- Mass Distortion Index
- Relational Waves
- Collapse Predictor
- Fraud Evolution
- Guardian Swarm



## Visualización avanzada + Demo Killers
Esta versión agrega:
- `/api/rfdc/graph`
- `/api/demo/run/<demo_id>`

Y dos secciones nuevas en el dashboard:
- `Graph + Waves + Dark Matter`
- `Demo Killers Studio`

Con esto puedes:
- visualizar MDI / clusters ocultos / ondas sobre el grafo
- correr The Invisible Network
- correr The Invisible Storm
- correr The Coming Collapse
