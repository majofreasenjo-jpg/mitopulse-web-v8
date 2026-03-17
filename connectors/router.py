from pathlib import Path
import json
from rest_connector import run_rest_connector
from websocket_connector import run_websocket_connector
from file_drop_connector import run_file_drop_connector

def run_config(cfg_path: Path):
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    kind = cfg.get("type")
    if kind == "rest":
        run_rest_connector(cfg)
    elif kind == "websocket":
        run_websocket_connector(cfg)
    elif kind == "file_drop":
        run_file_drop_connector(cfg)
    else:
        print(f"[skip] unknown connector type: {kind}")

def main():
    config_dir = Path("connectors/configs")
    configs = sorted(config_dir.glob("*.json"))
    for cfg in configs:
        run_config(cfg)

if __name__ == "__main__":
    main()
