@echo off
echo ====================================
echo Fixing NumPy Compatibility Issue
echo ====================================
echo.

echo Checking current NumPy version...
python -c "import numpy; print(f'Current NumPy: {numpy.__version__}')" 2>nul
if errorlevel 1 (
    echo NumPy not found or import failed
)

echo.
echo Uninstalling incompatible NumPy...
pip uninstall -y numpy

echo.
echo Installing compatible NumPy 1.x...
pip install "numpy<2"

echo.
echo Verifying installation...
python -c "import numpy; print(f'New NumPy: {numpy.__version__}')"
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

echo.
echo ====================================
echo Done! Try starting the backend again.
echo ====================================
pause
