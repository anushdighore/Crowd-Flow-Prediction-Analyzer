@echo off
echo Starting Crowd Counter Application...
echo.

REM Start Backend Server
echo Starting Backend Server...
cd backend

REM Set Python cache prefix to target/pycache
set PYTHONPYCACHEPREFIX=target/pycache

REM Load environment variables from .env
if exist .env (
    echo Loading backend .env configuration...
    for /f "usebackq tokens=1,* delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" set %%a=%%b
    )
) else (
    echo Warning: .env file not found in backend
)

REM Default values
if not defined API_HOST set API_HOST=0.0.0.0
if not defined API_PORT set API_PORT=8000

echo.
echo Cache directory: %PYTHONPYCACHEPREFIX%
echo Backend API will run on: http://%API_HOST%:%API_PORT%
echo.

REM Start backend uvicorn server
start "Backend Server" cmd /k "python -m uvicorn app.main:app --host %API_HOST% --port %API_PORT% --reload"

REM Start Frontend Server
echo.
echo Starting Frontend Server...
cd ..\frontend
start "Frontend Server" cmd /k "npm start"

echo.
echo Both servers are starting in separate windows.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
cd ..
echo.
echo Press any key to close this window...
pause > nul