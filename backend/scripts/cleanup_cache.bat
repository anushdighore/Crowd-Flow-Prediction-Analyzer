@echo off
REM Cleanup Script for Backend
REM Removes scattered cache files and consolidates them in target/

echo 🧹 Cleaning up backend cache files...

REM Remove existing __pycache__ directories
echo Removing __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM Remove existing .pytest_cache
echo Removing .pytest_cache...
if exist ".pytest_cache" rd /s /q ".pytest_cache"

REM Remove Python compiled files
echo Removing .pyc files...
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

REM Create target directory if not exists
if not exist "target" mkdir "target"
if not exist "target\pycache" mkdir "target\pycache"
if not exist "target\.pytest_cache" mkdir "target\.pytest_cache"

echo ✅ Cleanup complete!
echo.
echo 📦 Cache will now be stored in:
echo    - target/pycache/          (Python bytecode)
echo    - target/.pytest_cache/    (Pytest cache)
echo.
echo 💡 To apply settings, run:
echo    set PYTHONPYCACHEPREFIX=target/pycache
echo    OR add to .env and use python-dotenv
pause
