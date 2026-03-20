#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python - <<'PY'
from pathlib import Path
import json
from connectors.websocket_connector import run_websocket_connector
cfg = json.loads(Path("connectors/configs/ws_crypto_demo.json").read_text(encoding="utf-8"))
run_websocket_connector(cfg)
PY
