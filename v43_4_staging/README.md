# MitoPulse v43.4 Enterprise Hardening

Includes:
- auth + roles
- tenant isolation
- audit logs
- live connectors
- sandbox actions
- local + Render deploy
- tabs separated for usability

Run local:
cp .env.example .env
pip install -r requirements.txt
uvicorn backend.main:app --reload

Render:
Use render.yaml
