# 🚀 Installation Priority Guide

## ✅ Phase 1: MUST HAVE (Already Done)

These are already installed based on your previous dependency check:

```bash
✅ Python 3.9.23
✅ torch
✅ torchvision
✅ fastapi
✅ uvicorn
✅ python-multipart
✅ opencv-python
✅ pillow
✅ numpy (downgraded to <2)
✅ websockets
✅ Node.js v22.20.0
✅ Frontend dependencies (node_modules)
✅ Model checkpoint: checkpoints/jhu_5.pth
```

**Status**: ✅ **READY TO USE VMamba-TMTB NOW!**

---

## 🎯 Phase 2: RECOMMENDED (5 minutes)

### Install YOLOv8 Support

This gives you a second model to compare with:

```bash
# Activate environment
conda activate crowdenv

# Install YOLOv8
pip install ultralytics

# Verify installation
python -c "from ultralytics import YOLO; print('YOLOv8 ready!')"
```

**Why?**

- Auto-downloads checkpoint
- Very fast for real-time use
- Great for comparison with VMamba
- Easy to set up

**Status after this**: ✅ **2 MODELS WORKING** (VMamba + YOLOv8)

---

## 📦 Phase 3: OPTIONAL (For Additional Models)

### Install Additional Dependencies

Only if you want CSRNet or MCNN:

```bash
# These models use existing dependencies
# Just need checkpoints (see Phase 4)
```

No additional Python packages needed for CSRNet and MCNN!

---

## 🎨 Phase 4: FUTURE (Download Checkpoints)

### CSRNet Checkpoint

**Option A: Download Pre-trained**

```bash
# Look for CSRNet checkpoints at:
# - GitHub repositories
# - Model zoos
# - Research paper supplementary materials

# Save to: checkpoints/csrnet.pth
```

**Option B: Train Your Own**

```python
# Use models/csrnet.py
# Train on your crowd counting dataset
# Save checkpoint
```

### MCNN Checkpoint

**Option A: Download Pre-trained**

```bash
# Look for MCNN checkpoints at:
# - GitHub repositories (original paper implementation)
# - Crowd counting benchmarks

# Save to: checkpoints/mcnn.pth
```

**Option B: Train Your Own**

```python
# Use models/mcnn.py
# Lightweight - trains quickly
# Save checkpoint
```

---

## 🔄 Quick Installation Commands

### Full Setup (Fresh Installation)

```bash
# 1. Create environment (if not exists)
conda create -n crowdenv python=3.9
conda activate crowdenv

# 2. Install core dependencies
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install fastapi uvicorn[standard] python-multipart websockets pydantic
pip install opencv-python pillow "numpy<2"

# 3. Install YOLOv8 (recommended)
pip install ultralytics

# 4. Install frontend dependencies
cd crowd-counter-frontend
npm install
cd ..
```

### Update Existing Installation

```bash
# If you already have most packages, just add:
conda activate crowdenv
pip install ultralytics  # For YOLOv8
pip install pydantic     # For API models
```

---

## 📋 Dependency Check Commands

### Verify Python Packages

```bash
conda activate crowdenv
python check_dependencies.py
```

### Check Individual Packages

```bash
# Check PyTorch + CUDA
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"

# Check FastAPI
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"

# Check OpenCV
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"

# Check YOLOv8
python -c "from ultralytics import YOLO; print('YOLOv8: OK')"
```

### Check Frontend

```bash
cd crowd-counter-frontend
npm list --depth=0
```

---

## 🎯 Installation Priority Summary

### Priority 1: ⭐⭐⭐⭐⭐ (CRITICAL)

```bash
Status: ✅ COMPLETE
- Core Python packages (torch, fastapi, etc.)
- VMamba checkpoint
- Frontend dependencies
```

### Priority 2: ⭐⭐⭐⭐ (HIGHLY RECOMMENDED)

```bash
Action needed: pip install ultralytics
- YOLOv8 support
- Second model for comparison
- Real-time capability
Time: 2-3 minutes
```

### Priority 3: ⭐⭐⭐ (NICE TO HAVE)

```bash
Status: Optional
- CSRNet checkpoint (download/train)
- MCNN checkpoint (download/train)
- Additional model architectures
Time: Variable (depends on source)
```

---

## 🚦 Current Status

Based on your dependency check output:

```
✅ Python 3.9.23
✅ All core packages installed
✅ CUDA available (RTX 3050)
✅ Model checkpoint present
✅ Frontend ready
⚠️  npm needs attention (but Node.js works)
```

### To Start Using NOW:

```bash
# Option 1: Batch script
start_multimodel.bat

# Option 2: Manual
# Terminal 1:
conda activate crowdenv
python webcam_app_multimodel.py

# Terminal 2:
cd crowd-counter-frontend
npm start
```

---

## 🎨 Frontend Update (Optional)

If you want the new multi-model UI:

```bash
cd crowd-counter-frontend/src

# Backup original
copy App.js App_original.js
copy App.css App_original.css

# Use new multi-model version
copy App_multimodel.js App.js
copy App_multimodel.css App.css
```

**Or** keep both and switch by importing different files.

---

## 🐛 Common Issues & Fixes

### Issue 1: NumPy Version Conflict

```bash
ERROR: opencv-python requires numpy>=2

Fix:
pip install "numpy<2"
# Ignore the opencv warning - it will work fine
```

### Issue 2: YOLOv8 Not Found

```bash
ModuleNotFoundError: No module named 'ultralytics'

Fix:
conda activate crowdenv
pip install ultralytics
```

### Issue 3: Frontend Won't Start

```bash
npm ERR! missing script: start

Fix:
cd crowd-counter-frontend
npm install
npm start
```

### Issue 4: CUDA Not Detected

```bash
torch.cuda.is_available() returns False

Fix:
1. Install CUDA toolkit (match PyTorch version)
2. Or reinstall PyTorch with CUDA:
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

---

## 📊 What You Can Do RIGHT NOW

### Scenario 1: Just Want to Test

```bash
# You have everything needed!
start_multimodel.bat
# or
python webcam_app_multimodel.py
```

### Scenario 2: Want YOLOv8 Too

```bash
# 1. Install (2 minutes)
pip install ultralytics

# 2. Start system
start_multimodel.bat

# 3. Select YOLOv8 in web UI
```

### Scenario 3: Want All Models

```bash
# 1. Install YOLOv8
pip install ultralytics

# 2. Download/train CSRNet checkpoint
# 3. Download/train MCNN checkpoint

# 4. Start system
start_multimodel.bat
```

---

## 🎯 Recommended Path

### For Most Users:

```
Day 1 (Now):
✅ Use VMamba-TMTB (already working)
✅ Test with your images/videos
✅ Evaluate performance

Day 2 (Optional):
📦 Install YOLOv8: pip install ultralytics
🔄 Compare VMamba vs YOLOv8
📊 Choose best for your use case

Future (If needed):
📥 Download CSRNet/MCNN checkpoints
🎓 Train custom models
🔧 Fine-tune on your data
```

---

## 📞 Quick Reference

### Essential Commands

```bash
# Activate environment
conda activate crowdenv

# Check dependencies
python check_dependencies.py

# Start system
start_multimodel.bat

# Or manual:
python webcam_app_multimodel.py  # Backend
cd crowd-counter-frontend && npm start  # Frontend

# Install YOLOv8
pip install ultralytics

# Test imports
python -c "import torch, fastapi, cv2, ultralytics; print('All OK!')"
```

### Essential URLs

```
Backend:     http://localhost:8000
API Docs:    http://localhost:8000/docs
Frontend:    http://localhost:3000
Models API:  http://localhost:8000/api/models
Health:      http://localhost:8000/health
```

---

## ✅ Final Checklist

Before starting:

- [x] Python 3.9+ installed
- [x] Conda environment created
- [x] Core packages installed
- [x] VMamba checkpoint present
- [x] Frontend dependencies ready
- [ ] YOLOv8 installed (optional but recommended)
- [ ] Additional checkpoints (optional)

You're ready to go! 🚀

**Next step: Run `start_multimodel.bat`**
