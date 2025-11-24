@echo off
echo ========================================
echo Installing PedPy Dependencies
echo ========================================

cd backend

echo.
echo Installing pedpy, pandas, and scipy...
pip install pedpy>=1.0.0 pandas>=1.3.0 scipy>=1.7.0

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo PedPy and dependencies have been installed.
echo You can now use advanced crowd analysis features.
echo.
pause
