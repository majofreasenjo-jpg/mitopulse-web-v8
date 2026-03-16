
import sqlite3
from pathlib import Path
from typing import Optional, Any, Dict, List, Tuple

DB_PATH = Path(__file__).resolve().parent.parent.parent / "mitopulse_v2.db"

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    conn = get_conn()
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()

def q(conn, query: str, params: Tuple=()):
    cur = conn.execute(query, params)
    return cur

def fetchone(conn, query: str, params: Tuple=()):
    cur = conn.execute(query, params)
    row = cur.fetchone()
    return dict(row) if row else None

def fetchall(conn, query: str, params: Tuple=()):
    cur = conn.execute(query, params)
    rows = cur.fetchall()
    return [dict(r) for r in rows]
