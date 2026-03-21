import sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "seeds" / "protocol_v62.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
