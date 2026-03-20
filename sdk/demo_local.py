
import csv, secrets, base64, os
from engine import MitoPulseEngine, Sample, Env, iso_to_ts

def get_secret():
    if os.path.exists(".device_secret"):
        return open(".device_secret").read().strip()
    raw = base64.b64encode(secrets.token_bytes(32)).decode()
    open(".device_secret","w").write(raw)
    return raw

secret = get_secret()
engine = MitoPulseEngine(secret)

with open("sample.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        s = Sample(
            ts=iso_to_ts(row["timestamp"]),
            hr=float(row["hr"]),
            hrv_rmssd=float(row["hrv_rmssd"]),
            spo2=float(row["spo2"]),
            sleep_score=float(row["sleep_score"]),
            accel_load=float(row["accel_load"]),
            env=Env(
                altitude_m=float(row["altitude_m"]),
                temp_c=float(row["temp_c"]),
                humidity_pct=float(row["humidity_pct"])
            )
        )
        out = engine.process(s)
        print(out)
