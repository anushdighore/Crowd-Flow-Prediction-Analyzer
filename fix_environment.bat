@echo off
echo ========================================
echo Fixing NumPy and OpenCV (Proper Versions)
echo ========================================
echo.

echo Step 1: Checking current environment...
python -c "import sys; print('Python:', sys.version)"
echo.

echo Step 2: Uninstalling incompatible packages...
pip uninstall -y numpy opencv-python
echo.

echo Step 3: Installing NumPy ^<2 (compatible with PyTorch)...
pip install "numpy<2"
echo.

echo Step 4: Installing compatible OpenCV (4.8.x works with NumPy 1.x)...
pip install "opencv-python>=4.8.0,<4.10.0"
echo.

echo Step 5: Verifying installation...
echo.
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
python -c "import numpy; print('NumPy:', numpy.__version__); assert int(numpy.__version__.split('.')[0]) < 2, 'NumPy must be < 2.0'"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
echo.

echo Step 6: Testing all packages together...
python -c "import torch; import numpy as np; import cv2; print('✓ All packages compatible')"
echo.

echo ========================================
echo Done! Environment fixed with correct versions.
echo ========================================
pause
