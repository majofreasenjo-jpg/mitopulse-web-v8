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
