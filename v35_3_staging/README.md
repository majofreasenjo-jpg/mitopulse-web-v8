
MitoPulse v35.3 Production Layer

Includes:
- authentication (admin, analyst, client)
- webhook simulation
- persistent reports
- endpoints:
/login
/alert
/history

Run:
pip install -r requirements.txt
uvicorn app.main:app --reload
