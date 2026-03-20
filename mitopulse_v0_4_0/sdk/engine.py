
import hashlib, hmac, base64, time

class MitoPulseEngine:

    def __init__(self, secret):
        self.secret = secret.encode()

    def compute_index(self, hr, hrv=None):
        if hrv:
            tier = "tier2"
            idx = (hrv / 100)
        else:
            tier = "tier1"
            idx = (hr / 200)
        return idx, tier

    def generate_id(self, user_id, device_id, idx):
        ts = int(time.time())
        raw = f"{user_id}:{device_id}:{ts}:{idx}".encode()
        mac = hmac.new(self.secret, raw, hashlib.sha256).digest()
        dynamic_id = base64.urlsafe_b64encode(mac).decode().rstrip("=")
        signature = base64.urlsafe_b64encode(mac).decode().rstrip("=")
        return dynamic_id, signature, ts
