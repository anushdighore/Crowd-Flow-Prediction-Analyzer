@echo off
echo ========================================
echo CSRNet Fine-Tuning Pipeline
echo ========================================
echo.

set PROJECT_ROOT=D:\College\Major Project

cd /d "%PROJECT_ROOT%"

:menu
echo.
echo Choose an option:
echo [1] Generate Density Maps
echo [2] Test Dataset Loading
echo [3] Start Training
echo [4] Monitor Training (TensorBoard)
echo [5] Evaluate Model
echo [6] Open Test Notebook
echo [7] View Training Config
echo [0] Exit
echo.

set /p choice="Enter choice: "

if "%choice%"=="1" goto generate_density
if "%choice%"=="2" goto test_dataset
if "%choice%"=="3" goto start_training
if "%choice%"=="4" goto tensorboard
if "%choice%"=="5" goto evaluate
if "%choice%"=="6" goto notebook
if "%choice%"=="7" goto view_config
if "%choice%"=="0" goto end

echo Invalid choice!
goto menu

:generate_density
echo.
echo [1] Generating density maps...
python ml\src\csrnet\training\generate_density_maps.py
echo.
echo Done! Press any key to return to menu...
pause > nul
goto menu

:test_dataset
echo.
echo [2] Testing dataset loading...
python ml\src\csrnet\training\dataset.py
echo.
echo Done! Press any key to return to menu...
pause > nul
goto menu

:start_training
echo.
echo [3] Starting CSRNet training...
echo This may take several hours depending on your GPU.
echo.
set /p confirm="Continue? (Y/N): "
if /i "%confirm%"=="Y" (
    set /p quick="Run quick 1-epoch smoke test? (Y/N): "
    if /i "%quick%"=="Y" (
        python ml\src\csrnet\training\train.py --config ml\csrnet_config.yaml --epochs 1
    ) else (
        python ml\src\csrnet\training\train.py --config ml\csrnet_config.yaml
    )
)
echo.
echo Done! Press any key to return to menu...
pause > nul
goto menu

:tensorboard
echo.
echo [4] Starting TensorBoard...
echo Opening browser at http://localhost:6006
start http://localhost:6006
tensorboard --logdir ml\src\csrnet\training\logs\tensorboard
echo.
echo Press any key to return to menu...
pause > nul
goto menu

:evaluate
echo.
echo [5] Evaluating CSRNet model...
echo.
echo Available checkpoints:
dir /b ml\fine-tunned\csrnet\*.pth 2>nul
if errorlevel 1 (
    echo No checkpoints found!
    goto menu
)
echo.
set /p ckpt_name="Enter checkpoint filename: "
python ml\src\csrnet\training\evaluate.py --checkpoint ml\fine-tunned\csrnet\%ckpt_name% --visualize --samples 5
echo.
echo Done! Press any key to return to menu...
pause > nul
goto menu

:notebook
echo.
echo [6] Opening test notebook...
jupyter notebook ml\src\utils\csrnet_training_test.ipynb
echo.
pause
goto menu

:view_config
echo.
echo [7] Training Configuration:
echo ========================================
type ml\csrnet_config.yaml
echo ========================================
echo.
echo Press any key to return to menu...
pause > nul
goto menu

:end
echo.
echo Goodbye!
exit /b 0
