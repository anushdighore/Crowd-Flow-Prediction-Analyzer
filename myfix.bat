@echo off
echo ========================================
echo Installing from requirements.txt specs
echo ========================================

echo Uninstalling conflicting versions...
pip uninstall -y torch torchvision torchaudio numpy opencv-python

echo Installing PyTorch 2.5.1 + matching torchvision...
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121

echo Installing numpy<2 (as per requirements.txt)...
pip install "numpy<2"

echo Installing opencv-python 4.10 (compatible with numpy<2)...
pip install "opencv-python>=4.8.0,<4.11.0"

echo Installing other requirements...
pip install -r requirements.txt

echo Done!
pause
