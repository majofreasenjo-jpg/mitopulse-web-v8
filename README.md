# MitoPulse Master Pilot Platform v10

Build maestra que fusiona:
- lógica operativa multi-tenant
- upload real
- casos y auditoría
- simulaciones por industria y tamaño
- comparación baseline vs bio-inspired
- evidencia comercial para pilotos

## Ejecutar
```bash
cp .env.example .env
pip install -r requirements.txt
python run.py
```

Abrir:
`http://127.0.0.1:8000`

## Escenarios incluidos
- bank_small / medium / large
- marketplace_small / medium / large
- telco_small / medium / large

## Flujo recomendado
1. Generar token
2. Cargar escenario demo
3. Guardar corrida
4. Crear case
5. Subir dataset real de cliente
