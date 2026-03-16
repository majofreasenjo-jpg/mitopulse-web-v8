# ¿Esto queda todo en la web?

No.

## Correcto
- Frontend web: solo interfaz.
- Backend: recibe archivos, valida, procesa, construye el grafo.
- Storage: carpetas del servidor + base de datos.
- Producción: PostgreSQL + storage seguro.

## Cómo se arma la base del cliente
No partes de una tabla única.
Partes de 4 datasets:

1. customers.csv
2. devices.csv
3. events.csv
4. signals.csv

Luego MitoPulse los transforma en:
- nodos
- relaciones
- señales
- métricas
