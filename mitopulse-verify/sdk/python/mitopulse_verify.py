import requests
from typing import Dict, Any

class MitoPulseVerifer:
    """
    Official Python SDK for MitoPulse Verify (B2B SaaS).
    Used by your backend to request human presence verification.
    """
    def __init__(self, api_key: str, env: str = "production"):
        self.api_key = api_key
        self.base_url = "https://api.luxen.cl/v1" if env == "production" else "http://localhost:8000/v1"

    def verify(self, tenant_id: str, payload_from_client: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calls the Verify Engine to analyze the cryptographic and behavioral payload.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        request_body = {
            "tenant_id": tenant_id,
            "device_id": payload_from_client.get("device_id"),
            "timestamp": payload_from_client.get("timestamp"),
            "nonce": payload_from_client.get("nonce"),
            "signature": payload_from_client.get("signature"),
            "context": context
        }

        response = requests.post(f"{self.base_url}/verify", json=request_body, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"MitoPulse Verify Error: {response.text}")

        return response.json()

# Example Usage:
# mp = MitoPulseVerifer(api_key="pk_live_...")
# result = mp.verify("tenant_123", client_payload, {"tx_amount": 50000})
# if result['verified']: approve_transaction()
