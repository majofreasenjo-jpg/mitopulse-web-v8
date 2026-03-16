
# MitoPulse v16 – Trust Propagation Engine

Esta versión introduce **propagación de riesgo en el grafo**.

Un nodo sospechoso puede transmitir riesgo a sus vecinos
según:

• nivel de confianza entre nodos  
• factor de decaimiento  
• profundidad de propagación  

Esto permite modelar:

• estafas en cadena  
• contagio de fraude  
• nodos comprometidos  
• exposición indirecta  

## Ejecutar

pip install fastapi uvicorn

uvicorn app.main:app --reload

Abrir:

http://localhost:8000/docs
