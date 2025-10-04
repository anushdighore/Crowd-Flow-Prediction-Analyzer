@echo off
echo ========================================
echo   VMamba-TMTB Crowd Counter Launcher
echo   Image Upload Mode
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Starting Backend API Server...
echo.
start "Backend Server" cmd /k "python fastapi_app.py"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo [2/3] Starting Frontend React Server...
echo.
cd crowd-counter-frontend
start "Frontend Server" cmd /k "npm start"

echo.
echo [3/3] Servers started successfully!
echo.
echo ========================================
echo   Access the application at:
echo   http://localhost:3000
echo ========================================
echo.
echo   Backend API: http://localhost:8000
echo   Health Check: http://localhost:8000/health
echo.
echo   Press any key to stop all servers...
pause >nul

REM Kill the processes when done
echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq Backend Server*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend Server*" /T /F >nul 2>&1

echo Servers stopped.
pause
