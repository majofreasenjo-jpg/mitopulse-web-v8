
import base64, hashlib, hmac, json, math
from dataclasses import dataclass
from datetime import datetime

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def linear_norm(x, lo, hi):
    if hi <= lo:
        return 0.5
    return clamp((x - lo) / (hi - lo), 0.0, 1.0)

def iso_to_ts(iso):
    try:
        return int(datetime.fromisoformat(iso.replace("Z","+00:00")).timestamp())
    except:
        return int(float(iso))

@dataclass
class Env:
    altitude_m: float = 0
    temp_c: float = 22
    humidity_pct: float = 50
    pressure_hpa: float = 1013

@dataclass
class Sample:
    ts: int
    hr: float = None
    hrv_rmssd: float = None
    spo2: float = None
    sleep_score: float = None
    accel_load: float = None
    env: Env = None

class MitoPulseEngine:
    def __init__(self, secret_b64):
        self.secret = base64.b64decode(secret_b64.encode())
        self.series = []
        self.window_days = 60

    def compute_cenv(self, env):
        if not env:
            return 1.0
        adj = 1.0 / (1.0 + 0.012*(env.altitude_m/1000) + 0.008*abs(env.temp_c-22) + 0.005*abs(env.humidity_pct-50))
        return clamp(adj, 0.85, 1.15)

    def compute_index(self, s):
        weights = {"hrv":0.45,"spo2":0.25,"sleep":0.15,"load":0.15}
        feats = {}

        if s.hrv_rmssd: feats["hrv"] = linear_norm(s.hrv_rmssd,10,150)
        if s.spo2: feats["spo2"] = linear_norm(s.spo2,80,100)
        if s.sleep_score: feats["sleep"] = linear_norm(s.sleep_score,0,100)
        if s.accel_load: feats["load"] = 1 - linear_norm(s.accel_load,0,10)

        num = sum(weights[k]*feats[k] for k in feats if k in weights)
        den = sum(weights[k] for k in feats if k in weights)
        fused = num/den if den>0 else 0.5

        cenv = self.compute_cenv(s.env)
        return fused * cenv

    def update_series(self, ts, index):
        self.series.append((ts,index))
        cutoff = ts - self.window_days*86400
        self.series = [(t,v) for t,v in self.series if t>=cutoff]

    def build_vector(self):
        vals = [v for _,v in self.series]
        if not vals: vals=[0.5]
        mean = sum(vals)/len(vals)
        var = sum((x-mean)**2 for x in vals)/max(1,len(vals)-1)
        std = math.sqrt(var)
        slope = (vals[-1]-vals[0])/len(vals) if len(vals)>1 else 0
        return {"mean":mean,"std":std,"slope":slope,"last":vals[-1]}

    def dynamic_id(self, vector):
        msg = json.dumps(vector,sort_keys=True).encode()
        mac = hmac.new(self.secret,msg,hashlib.sha256).digest()
        return base64.urlsafe_b64encode(mac).decode().rstrip("=")

    def process(self,sample):
        idx = self.compute_index(sample)
        self.update_series(sample.ts,idx)
        vector = self.build_vector()
        dyn = self.dynamic_id(vector)
        return {"index":idx,"vector":vector,"dynamic_id":dyn}
