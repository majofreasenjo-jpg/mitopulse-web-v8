# Despliegue cloud-only

## Render
- New Web Service -> subir este repositorio.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variable: `DATABASE_URL`

## Railway
- Crear proyecto Python.
- Asignar PostgreSQL gestionado.
- Exponer puerto 8000.
- Variable `DATABASE_URL` apuntando a PostgreSQL.

## Cloudflare + dominio
- CNAME `demo` -> host de Render/Railway.
- SSL Full/Strict.
- Opcional: WAF y rate limiting en Cloudflare.

## Qué queda fuera de tu PC
- Base de datos en PostgreSQL gestionado.
- App y API en Render/Railway.
- Frontend servido por el mismo backend.
