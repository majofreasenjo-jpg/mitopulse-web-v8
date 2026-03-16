# MitoPulse Web MVP v8.2

Versión con:
- node_id persistente en móvil y web
- registro real de nodos en backend
- pulse / heartbeat real
- cross pulses entre usuarios
- vista clara de red y grafo para socios
- cloud-only

## Requisito
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST/DB?sslmode=require

## Ejecutar
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg2://USER:PASSWORD@HOST/DB?sslmode=require'
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

## Rutas
- / dashboard ejecutivo
- /app app principal
- /node nodo móvil persistente
- /network mapa de red
- /simulator simulador
- /present presentación
