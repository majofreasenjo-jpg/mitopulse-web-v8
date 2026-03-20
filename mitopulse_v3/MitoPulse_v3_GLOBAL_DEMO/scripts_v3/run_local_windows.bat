@echo off
echo Backend:
echo   cd backend ^&^& python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt ^&^& python main.py
echo.
echo Webapp:
echo   cd webapp ^&^& npm install ^&^& npm run dev
