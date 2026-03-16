import time
import hashlib
import uuid
from typing import List, Dict

class LedgerService:
    """
    Immutable audit trail for all verification attempts.
    Crucial for B2B compliance and forensic analysis.
    """
    def __init__(self):
        # Mock in-memory ledger. Production uses PostgreSQL + append-only logs.
        self.chain: List[Dict] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        self.chain.append({
            "idx": 0,
            "ts": time.time(),
            "tenant_id": "SYSTEM",
            "device_id": "genesis",
            "action": "LEDGER_INIT",
            "detail": "Verification Ledger Initialized",
            "prev_hash": "0" * 64,
            "hash": self._hash_block("0" * 64, "SYSTEM", "genesis")
        })

    def _hash_block(self, prev_hash: str, tenant_id: str, action: str) -> str:
        payload = f"{prev_hash}{tenant_id}{action}{time.time()}".encode('utf-8')
        return hashlib.sha256(payload).hexdigest()

    def record_event(self, tenant_id: str, device_id: str, action: str, detail: str) -> str:
        """
        Records a verification event, linking it cryptographically to the previous event.
        Returns the unique Transaction ID.
        """
        prev_block = self.chain[-1]
        tx_id = f"tx_{uuid.uuid4().hex[:16]}"
        
        new_block = {
            "idx": len(self.chain),
            "tx_id": tx_id,
            "ts": time.time(),
            "tenant_id": tenant_id,
            "device_id": device_id,
            "action": action,
            "detail": detail,
            "prev_hash": prev_block["hash"],
        }
        
        new_block["hash"] = self._hash_block(new_block["prev_hash"], tenant_id, action)
        
        self.chain.append(new_block)
        print(f"[LEDGER] {action} | Tenant: {tenant_id} | Device: {device_id} | TX: {tx_id}")
        
        return tx_id
