import time
import requests

url = "https://mitopulse-web-v8.onrender.com/api/rfdc/graph"
print("Polling V20 API endpoint:", url)

for attempt in range(40):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"Success! Status Code: {response.status_code}")
            # Try to print a slice of the JSON
            j = response.json()
            if 'nodes' in j and 'links' in j:
                print(f"V20 Payload verified! Nodes: {len(j['nodes'])}, Links: {len(j['links'])}")
            else:
                print("Warning: JSON retrieved but structure differs:", list(j.keys()))
            break
        elif response.status_code == 503:
            print(f"Attempt {attempt+1}: 503 Service Unavailable (Deploying...)")
        elif response.status_code == 502:
            print(f"Attempt {attempt+1}: 502 Bad Gateway (Rebooting...)")
        else:
            print(f"Attempt {attempt+1}: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Attempt {attempt+1}: Connection Error: {e}")
    time.sleep(15)
else:
    print("Timeout waiting for deployment.")
