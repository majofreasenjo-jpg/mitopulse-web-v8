
# MitoPulse v14 – Explainability Engine

Esta versión introduce **Explainable Trust Decisions**.

Ahora cada evaluación incluye:

• Relationship Depth Score (RDS)
• Authority / Guardian Score (ASS)
• Shared Reality Score (SRS)
• Behavioral Score (SC)
• Fraud Exposure (FE)

Y además entrega **explicación humana** del porqué de la decisión.

Ejemplo de respuesta:

{
 "decision": "REVIEW",
 "trust_score": 63,
 "explanation": {
   "reasons": [
     "Moderate behavioral deviation",
     "Low shared reality between nodes"
   ]
 }
}

## Ejecutar local

pip install fastapi uvicorn
uvicorn app.main:app --reload

Servidor:
http://127.0.0.1:8000

Docs API:
http://127.0.0.1:8000/docs
