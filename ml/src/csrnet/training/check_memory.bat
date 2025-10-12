@echo off
echo ========================================
echo CSRNet GPU Memory Check
echo ========================================
echo.

call C:\Users\anush\anaconda3\Scripts\activate.bat
call conda activate crowdenv

echo Current GPU Status:
nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free --format=csv,noheader,nounits

echo.
echo Running Python memory check...
python check_gpu_memory.py

echo.
echo ========================================
echo Ready to train with batch_size=1
echo ========================================
pause
