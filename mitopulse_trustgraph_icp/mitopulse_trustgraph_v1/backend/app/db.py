from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Any, Dict

DB_PATH = Path(__file__).resolve().parent.parent / "mitopulse_trustgraph.db"

SCHEMA = r"""
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS tenants (
  tenant_id TEXT PRIMARY KEY,
  name TEXT,
  api_key TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS devices (
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  epoch INTEGER NOT NULL DEFAULT 1,
  tier_hint TEXT,
  shared_secret_b64 TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  last_seen_at INTEGER,
  status TEXT NOT NULL DEFAULT 'active',
  PRIMARY KEY (tenant_id, user_id, device_id)
);

CREATE TABLE IF NOT EXISTS replay_ids (
  tenant_id TEXT NOT NULL,
  request_id TEXT NOT NULL,
  seen_at INTEGER NOT NULL,
  PRIMARY KEY (tenant_id, request_id)
);

CREATE TABLE IF NOT EXISTS identity_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  epoch INTEGER NOT NULL,
  ts INTEGER NOT NULL,

  tier_used TEXT NOT NULL,
  index_value REAL NOT NULL,
  dynamic_id TEXT NOT NULL,

  risk INTEGER NOT NULL,
  coercion INTEGER NOT NULL,
  stability REAL NOT NULL,
  human_conf REAL NOT NULL,

  context_fp TEXT,
  payload_hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS identity_state (
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  epoch INTEGER NOT NULL,

  baseline_mean REAL,
  baseline_std REAL,
  stability_band REAL,
  last_dynamic_id TEXT,
  last_ts INTEGER,
  dormant_since INTEGER,

  PRIMARY KEY (tenant_id, user_id, device_id, epoch)
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id TEXT,
  user_id TEXT,
  device_id TEXT,
  request_id TEXT,
  action TEXT NOT NULL,
  outcome TEXT NOT NULL,
  detail TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS graph_edges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id TEXT NOT NULL,
  src_node TEXT NOT NULL,
  dst_node TEXT NOT NULL,
  edge_type TEXT NOT NULL, -- continuity | cohab | risk
  weight REAL NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS clusters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id TEXT NOT NULL,
  cluster_type TEXT NOT NULL, -- unit | work | context | attack
  label TEXT NOT NULL,
  score REAL NOT NULL,
  members_json TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_ts ON identity_events(tenant_id, ts);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_logs(tenant_id, created_at);
CREATE INDEX IF NOT EXISTS idx_edges_src ON graph_edges(tenant_id, src_node);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = connect()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def q(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> list[Dict[str, Any]]:
    cur = conn.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    return rows


def exec_(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> None:
    conn.execute(sql, params)
