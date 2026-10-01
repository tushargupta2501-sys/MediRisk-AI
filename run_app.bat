@echo off
echo ========================================================
echo Starting MediRisk AI - Cardiovascular Risk Intelligence
echo ========================================================

echo [1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...
start /B .\venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

timeout /t 2 /nobreak >nul

echo [2/2] Starting Streamlit 3D Floating Frontend on http://localhost:8501 ...
.\venv\Scripts\streamlit.exe run app.py --server.headless false --server.port 8501
