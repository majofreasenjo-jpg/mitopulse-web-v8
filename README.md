# MitoPulse Modular Institutional Platform v12

Plataforma modular de demostración y desarrollo para MitoPulse.

## Qué incluye
- arquitectura institucional modular
- perfiles activables por industria, tamaño y tipo de demo
- datasets por industria y tamaño
- Historical Scenario Lab con ventanas pre / mid / post crisis
- dashboard grande, claro y coherente para demos
- base ejecutable para seguir desarrollando el producto real

## Ejecutar
```bash
pip install -r requirements.txt
python run.py
```

Abrir en el navegador:

`http://127.0.0.1:8000`

## Qué puedes demostrar
- fintech / banco / marketplace / telco
- riesgo sistémico para banco central
- caso AFP / seguros / portafolio
- crisis históricas: subprime, crisis asiática, FTX

## Filosofía de ejecución
Una sola plataforma, múltiples perfiles.

No se construyen productos separados. Se activa o desactiva la capa analítica según:
- industria
- tamaño
- amenaza
- modo de demo

## Estructura principal
- `api/` endpoints FastAPI
- `engine/` motores base y runner modular
- `profiles/` configuraciones de demo
- `historical/` escenarios históricos
- `data/` datasets por industria y tamaño
- `templates/` dashboard institucional
- `docs/` arquitectura, datasets, runtime, matemática, demos
