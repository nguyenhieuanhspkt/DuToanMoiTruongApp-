@echo off
title DuToanMoiTruongApp - EVN Vinh Tan 4
color 0B
echo ==============================================================================
echo     DuToanMoiTruongApp - EVN VINH TAN 4
echo     He Thong Tham Dinh Du Toan Quan Trac Moi Truong 2026 (TT20 ^& VB 5691/EVN)
echo ==============================================================================
echo.

cd /d "%~dp0"

echo [1/2] Khoi dong Backend Python FastAPI (Port 8000)...
start "Backend Python Engine" /min python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

echo [2/2] Khoi dong Frontend Client Vite React 19 (Port 3000)...
cd frontend
start "Frontend React 19" /min npm run dev -- --open

echo.
echo ==============================================================================
echo     HE THONG DA KHOI DONG THANH CONG!
echo     - Backend API: http://127.0.0.1:8000/docs
echo     - Frontend UI: http://localhost:3000
echo ==============================================================================
exit
