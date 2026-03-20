
import os
import time
from engine import MitoPulseEngine
from client import MitoPulseClient

def main():
    # Configuration
    secret = "demo_secret_local" # Local secret for dynamic ID generation
    server_secret = os.getenv("MITOPULSE_SERVER_SECRET", "server_secret")
    
    user_id = "enterprise_user_001"
    device_id = "device_hq_01"
    
    engine = MitoPulseEngine(secret)
    client = MitoPulseClient(server_secret=server_secret)
    
    print("\n== v0.4.0 Enterprise Demo: Signature & Audit Logs ==")
    
    # 1. Compute Index (Tier 2 - with HRV)
    idx, tier = engine.compute_index(hr=72, hrv=45)
    dyn_id, signature, ts = engine.generate_id(user_id, device_id, idx)
    
    print(f"Computed: Index={idx:.3f} Tier={tier} TS={ts}")
    print(f"Generated Dynamic ID: {dyn_id}")
    print(f"Generated Signature: {signature}")
    
    # 2. Post Event
    print("\nPosting Identity Event...")
    res = client.post_identity_event(user_id, device_id, ts, dyn_id, tier)
    print(f"Backend Result: {res}")
    
    # 3. Verify
    print("\nVerifying Identity...")
    v_res = client.verify(user_id, device_id, ts, dyn_id, tier)
    print(f"Verification Result: {v_res}")
    
    # 4. Tamper Check (Negative test)
    print("\nTesting Tamper Detection (Simulating invalid signature)...")
    try:
        client.post_identity_event(user_id, device_id, ts, dyn_id, tier, signature="tampered_signature")
    except Exception as e:
        print(f"Successfully blocked: {e}")

if __name__ == "__main__":
    main()
