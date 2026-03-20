# MitoPulse v3 — Living Network (Executable Demo)

Prototype avanzado ejecutable (local) que extiende TrustGraph + ICP con:
- **Trust Graph “vivo”** (decaimiento de edges + clusters dinámicos)
- **Tiers degradables** (Tier0 passive / Tier1 phone / Tier2 wearable)
- **ICP** (migración de identidad entre dispositivos/epochs)
- **Group quorum verify** (políticas tipo “2 de 3”)
- **Recovery sin dispositivo antiguo** (recuperación por grupo de confianza)

Todo se ejecuta local y guarda solo **derivados** (no biometría cruda).

## Ejecutar (puerto 8000)

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Abrir:
- Dashboard: http://127.0.0.1:8000/dashboard
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

### Simulator (genera eventos + ICP + quorum + recovery)
```bash
cd scripts
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python simulate.py --base http://127.0.0.1:8000 --tenant demo
```
