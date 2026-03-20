
# MitoPulse v2.6 Prototype

New in v2.6
-----------
• LIVE MODE streaming  
• Identity State UI  
• Human Proof endpoint  
• Stability bands concept  
• Simplified demo architecture

Architecture
------------
PWA (React/Vite)
↓
FastAPI Backend
↓
Baseline + Stability Engine
↓
Human Confidence + Human Proof
↓
Dashboard

Run backend:

cd backend
pip install fastapi uvicorn
python main.py

Run webapp:

cd webapp
npm install
npm run dev
