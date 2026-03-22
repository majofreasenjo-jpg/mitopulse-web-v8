import time
import hashlib
import uuid
import sqlite3
import os
from typing import List, Dict

class LedgerService:
    """
    V78 Immutable audit trail for all verification attempts.
    Crucial for B2B compliance and forensic analysis.
    Now fully persistent using physical SQLite arrays.
    """
    def __init__(self, db_path="v78_ledger.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        # Establish persistence with physical storage
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ledger (
                    idx INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_id TEXT UNIQUE,
                    ts REAL,
                    tenant_id TEXT,
                    device_id TEXT,
                    action TEXT,
                    detail TEXT,
                    prev_hash TEXT,
                    hash TEXT
                )
            ''')
            # Genesis Block Bootstrap
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM ledger")
            if cur.fetchone()[0] == 0:
                self._create_genesis_block(conn)
            conn.commit()

    def _create_genesis_block(self, conn):
        ts = time.time()
        prev_hash = "0" * 64
        hash_val = self._hash_block(prev_hash, "SYSTEM", "LEDGER_INIT")
        conn.execute('''
            INSERT INTO ledger (idx, tx_id, ts, tenant_id, device_id, action, detail, prev_hash, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (0, "GENESIS_TX", ts, "SYSTEM", "genesis", "LEDGER_INIT", "Verification Ledger Initialized", prev_hash, hash_val))

    def _hash_block(self, prev_hash: str, tenant_id: str, action: str) -> str:
        payload = f"{prev_hash}{tenant_id}{action}{time.time()}".encode('utf-8')
        return hashlib.sha256(payload).hexdigest()

    def _get_last_block(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM ledger ORDER BY idx DESC LIMIT 1")
            return dict(cur.fetchone())

    def record_event(self, tenant_id: str, device_id: str, action: str, detail: str) -> str:
        """
        Records a verification event, linking it cryptographically to the previous event.
        Commits directly to the physical v78_ledger.db.
        """
        prev_block = self._get_last_block()
        tx_id = f"tx_{uuid.uuid4().hex[:16]}"
        ts = time.time()
        new_hash = self._hash_block(prev_block["hash"], tenant_id, action)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO ledger (tx_id, ts, tenant_id, device_id, action, detail, prev_hash, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tx_id, ts, tenant_id, device_id, action, detail, prev_block["hash"], new_hash))
            conn.commit()
            
        print(f"[V78 LEDGER] {action} | Tenant: {tenant_id} | Device: {device_id} | TX: {tx_id}")
        return tx_id

    @property
    def chain(self) -> List[Dict]:
        """
        Dynamically fetches the physical ledger chain for the End-to-End Orchestrator.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM ledger ORDER BY idx ASC")
            return [dict(row) for row in cur.fetchall()]
