# Live Connectors Quickstart

## 1. Instala dependencias
```bash
pip install -r requirements.txt
```

## 2. Mercado real por REST
```bash
bash scripts/run_live_rest_market.sh
```

## 3. Crypto real por WebSocket
```bash
bash scripts/run_live_ws_crypto.sh
```

## 4. Todos los conectores
```bash
bash scripts/run_live_connectors_all.sh
```

## 5. Carga el output en MitoPulse
Usa una carpeta dentro de:
- `live_output/yahoo_live_market`
- `live_output/binance_live_crypto`
- `live_output/file_drop_bank_demo`

Cada una ya respeta el formato canónico:
- customers.csv
- devices.csv
- events.csv
- signals.csv
