@echo off
REM Start Backend API with proper cache configuration

echo 🚀 Starting Backend API Server...
echo.

REM Set Python cache prefix to target/pycache
set PYTHONPYCACHEPREFIX=target/pycache

REM Load environment variables from .env
if exist .env (
    echo ✅ Loading .env configuration...
    for /f "usebackq tokens=1,* delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" set %%a=%%b
    )
) else (
    echo ⚠️  Warning: .env file not found
)

REM Default values
if not defined API_HOST set API_HOST=0.0.0.0
if not defined API_PORT set API_PORT=8000

echo.
echo 📦 Cache directory: %PYTHONPYCACHEPREFIX%
echo 🌐 API will run on: http://%API_HOST%:%API_PORT%
echo.

REM Start uvicorn
python -m uvicorn app.main:app --host %API_HOST% --port %API_PORT% --reload

pause
