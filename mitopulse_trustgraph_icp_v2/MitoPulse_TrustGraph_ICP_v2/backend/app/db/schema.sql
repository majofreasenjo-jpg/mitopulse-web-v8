
CREATE TABLE IF NOT EXISTS devices (
  device_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  pubkey_b64 TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tenants (
  tenant_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  policy_json TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS membership (
  tenant_id TEXT NOT NULL,
  group_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL,
  PRIMARY KEY (tenant_id, group_id, user_id)
);

CREATE TABLE IF NOT EXISTS identity_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  epoch INTEGER NOT NULL,
  ts INTEGER NOT NULL,
  tier TEXT NOT NULL,
  idx REAL NOT NULL,
  slope REAL NOT NULL,
  stability REAL NOT NULL,
  human_conf REAL NOT NULL,
  risk INTEGER NOT NULL,
  coercion INTEGER NOT NULL,
  packet_hash TEXT NOT NULL,
  request_id TEXT NOT NULL UNIQUE,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS identity_state (
  user_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  epoch INTEGER NOT NULL,
  last_ts INTEGER NOT NULL,
  mean_idx REAL NOT NULL,
  std_idx REAL NOT NULL,
  mean_hr REAL NOT NULL,
  std_hr REAL NOT NULL,
  stability_band REAL NOT NULL,
  hibernating INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  PRIMARY KEY (user_id, device_id, epoch)
);

CREATE TABLE IF NOT EXISTS trust_edges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  a_node TEXT NOT NULL,
  b_node TEXT NOT NULL,
  edge_type TEXT NOT NULL,
  weight REAL NOT NULL,
  meta_json TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  action TEXT NOT NULL,
  tenant_id TEXT,
  user_id TEXT,
  device_id TEXT,
  request_id TEXT,
  outcome TEXT NOT NULL,
  reason TEXT NOT NULL,
  meta_json TEXT NOT NULL
);
