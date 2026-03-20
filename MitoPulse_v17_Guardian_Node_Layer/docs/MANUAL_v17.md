
MANUAL RÁPIDO – MITOPULSE v17

1. Iniciar
uvicorn app.main:app --reload

2. Revisar guardianes
GET /guardians

3. Propagar riesgo
POST /propagate

Ejemplo:
{
  "infected_node": "nd_manu_01",
  "initial_risk": 85,
  "decay": 0.6
}

4. Evaluar decisión por guardianes
POST /guardian/evaluate

Ejemplo:
{
  "source_node": "nd_bruno_01",
  "target_node": "nd_carla_01",
  "risk_score": 72,
  "route": ["guardian_bank_01"]
}

5. El sistema devolverá:
- guardian_path
- decisiones de cada guardián
- decisión final
