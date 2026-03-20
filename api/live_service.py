from pathlib import Path
import json

from connectors.rest_connector import run_rest_connector
from connectors.websocket_connector import run_websocket_connector
from connectors.file_drop_connector import run_file_drop_connector

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "connectors" / "configs"

def list_live_configs():
    out = []
    for fp in sorted(CONFIG_DIR.glob("*.json")):
        cfg = json.loads(fp.read_text(encoding="utf-8"))
        out.append({
            "config_name": fp.stem,
            "type": cfg.get("type"),
            "source_name": cfg.get("source_name"),
            "output_dir": cfg.get("output_dir"),
            "symbols": cfg.get("symbols", []),
            "duration_seconds": cfg.get("duration_seconds")
        })
    return out

def run_live_config(config_name: str):
    fp = CONFIG_DIR / f"{config_name}.json"
    if not fp.exists():
        raise FileNotFoundError(f"Config not found: {config_name}")
    cfg = json.loads(fp.read_text(encoding="utf-8"))
    kind = cfg.get("type")
    if kind == "rest":
        run_rest_connector(cfg)
    elif kind == "websocket":
        run_websocket_connector(cfg)
    elif kind == "file_drop":
        run_file_drop_connector(cfg)
    else:
        raise ValueError(f"Unknown connector type: {kind}")
    return {
        "status": "ok",
        "config_name": config_name,
        "type": kind,
        "source_name": cfg.get("source_name"),
        "output_dir": cfg.get("output_dir")
    }
