
MANUAL DE USO – MITOPULSE v14

1. Iniciar servidor

uvicorn app.main:app --reload

2. Abrir interfaz automática

http://localhost:8000/docs

3. Ejecutar evaluación

POST /evaluate

ejemplo payload:

{
 "source_node_id": "nd_manu_01",
 "target_node_id": "ext_unknown_01",
 "amount_anomaly": 0.8,
 "routine_break": 0.7,
 "shared_reality": 25,
 "guardian_score": 40,
 "fraud_exposure": 20
}

4. El sistema responderá con:

• decisión
• trust score
• explicación detallada
