# MitoPulse Live Connectors v1 — Real Sources

Esta versión conecta MitoPulse con fuentes reales online.

## Incluye
### 1. Yahoo Finance (REST)
- precios en vivo
- cambio porcentual
- señales básicas de volatilidad

Script:
```bash
bash scripts/run_live_rest_market.sh
```

Output:
- `live_output/yahoo_live_market/customers.csv`
- `live_output/yahoo_live_market/devices.csv`
- `live_output/yahoo_live_market/events.csv`
- `live_output/yahoo_live_market/signals.csv`

### 2. Binance (WebSocket)
- trades en vivo
- señales básicas de liquidez

Script:
```bash
bash scripts/run_live_ws_crypto.sh
```

Output:
- `live_output/binance_live_crypto/...`

### 3. File drop batch
- para bancos / fintech / AFP
- deja CSVs en `connectors/inbox/`

## Cómo usarlo con el prototipo
1. corre uno de los scripts de ingestión live
2. revisa `live_output/<source>/`
3. apunta el dataset loader del prototipo a esa carpeta
4. ejecuta el perfil correspondiente

## Recomendación de pruebas
### simple
- Yahoo REST market

### intermedio
- Binance WebSocket

### institucional
- file drop con dataset propio

## Nota
La conexión real requiere internet al ejecutar el proyecto localmente.
