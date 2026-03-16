# MitoPulse Client Simulation Platform v4

Versión con upload real de archivos y persistencia de corridas.

## Qué resuelve
- La web no guarda la lógica: solo interfaz y API.
- Los CSV del cliente se suben al backend y se guardan en `uploads/`.
- Las corridas se persisten en base de datos (`sqlite` por defecto, `PostgreSQL` si configuras `DATABASE_URL`).

## Archivos requeridos por cliente
- customers.csv
- devices.csv
- events.csv
- signals.csv

## Ejecutar
```bash
cp .env.example .env
pip install -r requirements.txt
python run.py
```

Abrir:
`http://127.0.0.1:8000`

## PostgreSQL opcional
```bash
docker compose up -d
```
Luego cambia `DATABASE_URL` en `.env`.
