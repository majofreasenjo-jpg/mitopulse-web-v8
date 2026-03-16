
# MitoPulse Human Infrastructure v1

Capas:
1. Human Presence Engine
2. Global Trust Graph
3. Identity Continuity Network
4. Universal Developer API

## Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Ejemplos
```bash
cd examples
pip install -r requirements.txt
python post_demo_events.py
python continuity_demo.py
python group_verify_demo.py
```
