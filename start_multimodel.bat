@echo off
echo ========================================
echo  MULTI-MODEL CROWD COUNTER LAUNCHER
echo ========================================
echo.

REM Check if conda environment exists
call conda activate crowdenv 2>nul
if errorlevel 1 (
    echo [ERROR] Conda environment 'crowdenv' not found!
    echo Please create it first:
    echo   conda create -n crowdenv python=3.9
    echo   conda activate crowdenv
    pause
    exit /b 1
)

echo [OK] Conda environment activated: crowdenv
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python check_dependencies.py
if errorlevel 1 (
    echo.
    echo [WARNING] Some dependencies might be missing.
    echo Do you want to continue anyway? (Y/N)
    set /p continue=
    if /i not "%continue%"=="Y" (
        exit /b 1
    )
)

echo.
echo ========================================
echo  STARTING SERVERS
echo ========================================
echo.

REM Start backend server in new window
echo [1/2] Starting Multi-Model Backend Server...
start "Backend Server" cmd /k "conda activate crowdenv && python webcam_app_multimodel.py"

REM Wait for backend to initialize
echo Waiting for backend to initialize (5 seconds)...
timeout /t 5 /nobreak > nul

REM Start frontend server in new window
echo [2/2] Starting React Frontend...
cd crowd-counter-frontend
start "Frontend Server" cmd /k "npm start"
cd ..

echo.
echo ========================================
echo  SYSTEM STARTED!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend:     http://localhost:3000
echo.
echo Models API:   http://localhost:8000/api/models
echo WebSocket:    ws://localhost:8000/ws/count
echo.
echo ========================================
echo  AVAILABLE MODELS
echo ========================================
echo.
echo 1. VMamba-TMTB  (Density-based, High accuracy)
echo 2. CSRNet       (Density-based, Dense crowds)
echo 3. YOLOv8       (Detection-based, Real-time)
echo 4. MCNN         (Density-based, Multi-scale)
echo.
echo Select models from the web interface at:
echo http://localhost:3000
echo.
echo ========================================
echo  CONTROLS
echo ========================================
echo.
echo - Close this window to keep servers running
echo - Press Ctrl+C in server windows to stop them
echo - Or close the server windows directly
echo.
echo ========================================
echo.
echo Press any key to exit this launcher...
pause > nul
