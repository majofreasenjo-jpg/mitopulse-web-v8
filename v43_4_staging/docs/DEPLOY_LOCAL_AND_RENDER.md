# Deploy local + Render

## Local
cp .env.example .env
pip install -r requirements.txt
uvicorn backend.main:app --reload

## Render
- subir a GitHub
- conectar en Render
- usar render.yaml
- agregar variables:
  - OPENAI_API_KEY
  - AI_ENABLED
  - AUTH_ENABLED
  - TENANT_DEFAULT
