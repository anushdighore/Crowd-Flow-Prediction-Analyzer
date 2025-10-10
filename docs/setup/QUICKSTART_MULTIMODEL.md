# 🚀 Quick Start Guide - Multi-Model System

## Option 1: Fastest Start (Using Existing VMamba Model)

```bash
# 1. Activate environment
conda activate crowdenv

# 2. Start multi-model backend
python webcam_app_multimodel.py

# 3. In another terminal, start frontend
cd crowd-counter-frontend
npm start

# 4. Open browser: http://localhost:3000
```

## Option 2: Use Batch Script

```bash
# Simply run:
start_multimodel.bat
```

## Option 3: Test with YOLOv8 (No checkpoint needed)

YOLOv8 will auto-download on first use!

```bash
# 1. Install YOLOv8
pip install ultralytics

# 2. Start servers (same as Option 1)
python webcam_app_multimodel.py

# 3. In web interface, select "YOLOv8" model
```

---

## 📦 What You Have vs What You Need

### ✅ Already Available

- **VMamba-TMTB**: `checkpoints/jhu_5.pth` ✓
- **Core Dependencies**: torch, fastapi, opencv, etc. ✓
- **Frontend**: React app ready ✓

### 📥 Need to Download/Install

#### For YOLOv8 (Easiest):

```bash
pip install ultralytics
# Checkpoint downloads automatically!
```

#### For CSRNet:

```bash
# Model code is ready, just need checkpoint
# Download or train CSRNet model -> save to checkpoints/csrnet.pth
```

#### For MCNN:

```bash
# Model code is ready, just need checkpoint
# Download or train MCNN model -> save to checkpoints/mcnn.pth
```

---

## 🎯 Using the Web Interface

### 1. Model Selection

- Top of page shows "Select Model Architecture"
- Click on any model button to switch
- Active model has green background
- Unavailable models are grayed out

### 2. Modes

- **Upload Image**: Test with static images
- **Live Webcam**: Real-time counting

### 3. Results

- Count displayed in large numbers
- Performance metrics (FPS, timing)
- Density map statistics (for density-based models)

---

## 🔌 API Testing (Optional)

### List Available Models

```bash
curl http://localhost:8000/api/models
```

### Switch Model Programmatically

```bash
curl -X POST http://localhost:8000/api/select-model \
  -H "Content-Type: application/json" \
  -d '{"model_type": "yolov8"}'
```

### Check Health

```bash
curl http://localhost:8000/health
```

---

## 🐛 Quick Troubleshooting

### "Module not found" errors

```bash
pip install -r requirements_multimodel.txt
```

### NumPy version error

```bash
pip install "numpy<2"
```

### Frontend won't start

```bash
cd crowd-counter-frontend
npm install
npm start
```

### Model not loading

- Check `checkpoints/` folder for model files
- Start with YOLOv8 (auto-downloads)
- Or use VMamba-TMTB (already have checkpoint)

---

## 📂 File Reference

| File                       | Purpose                      |
| -------------------------- | ---------------------------- |
| `webcam_app_multimodel.py` | Multi-model backend server   |
| `models/model_factory.py`  | Model loading logic          |
| `models/csrnet.py`         | CSRNet architecture          |
| `models/yolov8_counter.py` | YOLOv8 wrapper               |
| `models/mcnn.py`           | MCNN architecture            |
| `App_multimodel.js`        | Frontend with model selector |
| `start_multimodel.bat`     | One-click launcher           |

---

## ⚡ Performance Tips

1. **Use GPU**: Much faster inference
2. **Start with YOLOv8**: Fastest setup, good for real-time
3. **VMamba-TMTB**: Best accuracy (already configured)
4. **Lower resolution**: For faster FPS in webcam mode

---

## 🎓 Next Steps

1. ✅ Get system running with VMamba or YOLOv8
2. 📥 Download additional model checkpoints as needed
3. 🧪 Test different models on your specific use case
4. 🔧 Fine-tune models with your own data
5. 📊 Compare performance across models

---

**Ready to start? Run: `start_multimodel.bat` or follow Option 1!** 🚀
