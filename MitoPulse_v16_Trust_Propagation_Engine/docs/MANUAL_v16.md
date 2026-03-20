
MANUAL RÁPIDO – MITOPULSE v16

1. Ejecutar servidor

uvicorn app.main:app --reload

2. Ir a:

http://localhost:8000/docs

3. Ejecutar endpoint:

POST /propagate

Ejemplo:

{
 "infected_node": "nd_manu_01",
 "initial_risk": 80,
 "decay": 0.6
}

El sistema propagará el riesgo a los nodos conectados
según su nivel de confianza.
