# MitoPulse MVP Prototype (Local‑First)

Contenido:
- **backend/**: FastAPI verifier (almacena **solo derivados**, nunca biometría cruda)
- **sdk/**: SDK Python que calcula índice + identidad dinámica localmente y envía derivados

## 1) Levantar backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Abre:
- Docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/dashboard

## 2) Instalar SDK y correr demo

```bash
cd sdk
python -m venv .venv
source .venv/bin/activate
pip install -e .
python demo_local.py
```

La demo:
- lee `sdk/sample.csv`
- calcula `mitopulse_index`, `slope` y `dynamic_id` localmente
- publica eventos derivados en el backend
- valida el último `dynamic_id`

## Notas de seguridad (MVP)

- El servidor **no conoce** el secreto del dispositivo → no puede recomputar `dynamic_id`.
- La verificación se hace por *matching* contra el **último** `dynamic_id` recibido.
- Anti‑replay: `/v1/verify` exige `request_id` (UUID) de un solo uso.
- Control de skew temporal con `MITOPULSE_ALLOWED_SKEW_SECONDS` (default 600s).


## 3) 3 niveles de cómputo (Tier 1/2/3)

Ver `docs/LEVELS.md`.
