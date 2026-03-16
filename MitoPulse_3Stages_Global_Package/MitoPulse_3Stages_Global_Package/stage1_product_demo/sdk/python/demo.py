import requests
base = "http://localhost:8000"
for u in ["manuel","sofia","carlos","ana","diego"]:
    for s,h,r in [(0.80,0.90,10),(0.82,0.92,8),(0.79,0.89,12)]:
        print(requests.post(f"{base}/v1/presence/event", json={"user_id":u,"device_id":f"mobile-{u}","stability":s,"human_conf":h,"risk_signal":r}).json())
print(requests.post(f"{base}/v1/verify/presence", json={"user_id":"manuel","device_id":"mobile-manuel","stability":0.81,"human_conf":0.91,"risk_signal":10}).json())
