# Deploy local + Render

## Local
```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## Render
- crea repo GitHub
- sube el proyecto
- crea nuevo Web Service en Render
- usa el `render.yaml`
- define las env vars:
  - OPENAI_API_KEY
  - AI_ENABLED
  - CLIENT_MODE
  - CONNECTOR_* que quieras activar
