import sys
import os
import time
import uuid

# Map the path to simulate SDK usage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'sdk', 'python')))
try:
    from mitopulse_verify import MitoPulseVerifer
except ImportError:
    print("MitoPulseVerifer SDK not found. Make sure paths are correct.")

print("==================================================================")
print("🏦 ACME BANK - CRITICAL TRANSACTION FLOW (MITOPULSE VERIFY INTEGRATION)")
print("==================================================================\n")

print("[1] User initiates a $50,000 wire transfer from their browser/app.")
print("[2] Browser automatically uses MitoPulse JS/Mobile SDK to cryptographically sign the intent...\n")

# Normally generated in JS (mitopulse.js) or Mobile (MitoPulseVerify.swift) by the user's device
mock_client_payload = {
    "device_id": "node_9185",
    "timestamp": time.time(),
    "nonce": uuid.uuid4().hex,
    "signature": "ZWRkOTRmMDNhYjg1NmI...", # Mock Ed25519 signature
}

print(f"    Payload generated on user device: {mock_client_payload['device_id']} with signature {mock_client_payload['signature'][:10]}...\n")

print("[3] Acme Bank Server receives payload and asks MitoPulse to verify human presence and coercion risk...\n")

# Acme Bank backend uses the Python SDK
try:
    # Initialize SDK with Acme Bank's secret key
    mp_client = MitoPulseVerifer(api_key="sk_live_12345", env="local")
    
    # Request Verification from the MitoPulse Gateway
    # Note: In a real simulation this would hit the FastAPI server on :8000
    print("    [API Call] POST /verify")
    print("    Awaiting MitoPulse Response...")
    
    time.sleep(1.5) # Simulate network lag
    
    # MOCK RESPONSE (Simulating what the FastAPI server would return)
    # Since the FastAPI server isn't explicitly running in this script, we mock the success.
    mock_response = {
        "verified": True,
        "confidence": 0.98,
        "risk_level": "LOW",
        "transaction_id": "tx_8f92a1b4e6c3d0f1"
    }
    
    print("\n✅ MITOPULSE RISKS ENGINE RESPONSE:")
    print(f"    - Verified:           {mock_response['verified']}")
    print(f"    - Human Confidence:   {mock_response['confidence'] * 100}%")
    print(f"    - Coercion Risk:      {mock_response['risk_level']}")
    print(f"    - Immutable Audit TX: {mock_response['transaction_id']}\n")
    
    if mock_response['verified'] and mock_response['risk_level'] == "LOW":
        print("[4] Acme Bank AUTHORIZES wire transfer safely. Funds released. 💸")
    else:
        print("[4] Acme Bank BLOCKS transfer due to high coercion risk. Account locked. 🔒")

except Exception as e:
    print(f"Verification Failed via SDK: {e}")
