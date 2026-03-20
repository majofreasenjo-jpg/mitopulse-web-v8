#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python - <<'PY'
from pathlib import Path
import json
from connectors.rest_connector import run_rest_connector
cfg = json.loads(Path("connectors/configs/rest_market_demo.json").read_text(encoding="utf-8"))
run_rest_connector(cfg)
PY
