from datetime import datetime
from mitopulse_protocol.storage.db import get_conn

def record_exchange(anchor_id: str, exchange_type: str, payload_summary: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO federation_exchanges(anchor_id,exchange_type,payload_summary,ts) VALUES (?,?,?,?)",
        (anchor_id, exchange_type, payload_summary, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
