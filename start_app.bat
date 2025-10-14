@echo off
echo Starting Crowd Counter Application...
echo.

echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Starting Frontend Server...
cd ..\frontend
start "Frontend Server" cmd /k "npm run start"

echo.
echo Both servers are starting in separate windows.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
cd ..
echo.
echo Press any key to close this window...
pause > nul