
# MitoPulse v11

Demo scaffold with:
- Dashboard
- Network / ecosystem map
- Node view with persistent node_id and heartbeats
- Simulator / audit mode
- Guardian nodes algorithm endpoint
- Fraud cluster and spread map endpoints

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/network
- http://127.0.0.1:8000/node
- http://127.0.0.1:8000/simulator
