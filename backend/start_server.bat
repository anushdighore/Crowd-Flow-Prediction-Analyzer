@echo off
echo Starting Crowd Counter Backend Server...
echo.
cd /d "%~dp0"
call conda activate crowdenv
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
