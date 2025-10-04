# Multi-Model Crowd Counting System - Setup Guide

## 📋 Overview

This system supports **multiple model architectures** for crowd counting:

1. **VMamba-TMTB** (Vision Mamba with Temporal-Multi-scale Token Block)
2. **CSRNet** (Congested Scene Recognition Network)
3. **YOLOv8** (Object Detection for Person Counting)
4. **MCNN** (Multi-Column CNN)

---

## 🔧 Installation

### 1. Base Dependencies

```bash
# Activate your conda environment
conda activate crowdenv

# Install core dependencies
pip install torch torchvision python-multipart opencv-python pillow numpy websockets fastapi uvicorn pydantic
```

### 2. Model-Specific Dependencies

#### For YOLOv8:

```bash
pip install ultralytics
```

#### For VMamba-TMTB (if using official implementation):

```bash
pip install timm einops
```

---

## 📦 Model Checkpoints

### Directory Structure

```
checkpoints/
├── jhu_5.pth          # VMamba-TMTB checkpoint
├── csrnet.pth         # CSRNet checkpoint
├── yolov8n.pt         # YOLOv8 checkpoint
└── mcnn.pth           # MCNN checkpoint
```

### Download Checkpoints

1. **VMamba-TMTB**: Already available at `./checkpoints/jhu_5.pth`

2. **CSRNet**: Download pre-trained CSRNet checkpoint

   - Save to: `./checkpoints/csrnet.pth`

3. **YOLOv8**:

   - Will auto-download on first use
   - Or download manually: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
   - Save to: `./checkpoints/yolov8n.pt`

4. **MCNN**: Download pre-trained MCNN checkpoint
   - Save to: `./checkpoints/mcnn.pth`

---

## 🚀 Running the Multi-Model System

### Method 1: Using the New Multi-Model App

```bash
# Start the multi-model backend
python webcam_app_multimodel.py
```

### Method 2: Create a Batch Script

Create `start_multimodel.bat`:

```batch
@echo off
echo ====================================
echo  Multi-Model Crowd Counter Launcher
echo ====================================

REM Activate conda environment
call conda activate crowdenv

REM Start backend
echo Starting multi-model backend...
start cmd /k "python webcam_app_multimodel.py"

REM Wait a few seconds
timeout /t 5

REM Start frontend
echo Starting React frontend...
cd crowd-counter-frontend
start cmd /k "npm start"

echo.
echo ====================================
echo  System Started!
echo ====================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ====================================
pause
```

---

## 🎯 Using the System

### 1. Start Both Servers

```bash
# Terminal 1: Backend
python webcam_app_multimodel.py

# Terminal 2: Frontend
cd crowd-counter-frontend
npm start
```

### 2. Access the Application

Open browser: `http://localhost:3000`

### 3. Select a Model

- Use the **model selector** at the top of the page
- Click on your preferred model architecture
- System will automatically load the selected model

### 4. Choose Mode

- **Upload Image**: Process static images
- **Live Webcam**: Real-time crowd counting

---

## 🔌 API Endpoints

### Get Available Models

```http
GET http://localhost:8000/api/models
```

Response:

```json
{
  "models": {
    "vmamba_tmtb": {
      "name": "VMamba-TMTB",
      "description": "Vision Mamba with Temporal-Multi-scale Token Block",
      "checkpoint": "./checkpoints/jhu_5.pth",
      "checkpoint_exists": true
    },
    "csrnet": { ... },
    "yolov8": { ... },
    "mcnn": { ... }
  },
  "current_model": "vmamba_tmtb"
}
```

### Switch Model

```http
POST http://localhost:8000/api/select-model
Content-Type: application/json

{
  "model_type": "yolov8"
}
```

### Get Current Model

```http
GET http://localhost:8000/api/current-model
```

### WebSocket for Real-Time Counting

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/count");

// Send frame
ws.send(
  JSON.stringify({
    frame: base64EncodedImage,
  })
);

// Receive result
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log("Count:", result.count);
};
```

---

## 📊 Model Comparison

| Model           | Type      | Speed     | Accuracy | Use Case                 |
| --------------- | --------- | --------- | -------- | ------------------------ |
| **VMamba-TMTB** | Density   | Fast      | High     | General crowd counting   |
| **CSRNet**      | Density   | Medium    | High     | Dense crowds             |
| **YOLOv8**      | Detection | Very Fast | Medium   | Sparse crowds, real-time |
| **MCNN**        | Density   | Fast      | Medium   | Multi-scale crowds       |

### When to Use Each Model:

- **VMamba-TMTB**: Best all-around performance, handles various crowd densities
- **CSRNet**: Best for very dense crowds with severe occlusion
- **YOLOv8**: Best for real-time applications with sparse to medium crowds
- **MCNN**: Good balance between speed and accuracy

---

## 🐛 Troubleshooting

### Model Not Loading

**Issue**: "Checkpoint not found"

```bash
# Check if checkpoint exists
dir checkpoints\

# Download missing checkpoints (see Download Checkpoints section)
```

### YOLOv8 Import Error

```bash
# Install ultralytics
pip install ultralytics

# Verify installation
python -c "from ultralytics import YOLO; print('Success!')"
```

### CUDA Out of Memory

```python
# Reduce batch size or use CPU
device = 'cpu'  # In webcam_app_multimodel.py
```

### NumPy Version Conflict

```bash
# Downgrade NumPy for PyTorch compatibility
pip install "numpy<2"
```

---

## 📝 Frontend Integration

### Update App.js

Replace your current `App.js` with `App_multimodel.js`:

```bash
cd crowd-counter-frontend/src
copy App_multimodel.js App.js
copy App_multimodel.css App.css
```

Or manually integrate the model selector component from `App_multimodel.js`.

---

## 🔄 Switching Between Single and Multi-Model

### Use Multi-Model System:

```bash
python webcam_app_multimodel.py
```

### Use Original System (VMamba only):

```bash
python webcam_app.py
```

---

## 📁 Complete Project Structure

```
Major Project/
├── models/
│   ├── model_factory.py      # Multi-model factory
│   ├── csrnet.py             # CSRNet implementation
│   ├── yolov8_counter.py     # YOLOv8 wrapper
│   ├── mcnn.py               # MCNN implementation
│   ├── vmamba_official.py    # VMamba official
│   └── vmamba_tmtb.py        # VMamba custom
├── checkpoints/
│   ├── jhu_5.pth             # VMamba checkpoint
│   ├── csrnet.pth            # CSRNet checkpoint
│   ├── yolov8n.pt            # YOLOv8 checkpoint
│   └── mcnn.pth              # MCNN checkpoint
├── utils/
│   ├── preprocess.py
│   ├── postprocess.py
│   └── visualize.py
├── webcam_app.py             # Original single-model app
├── webcam_app_multimodel.py  # New multi-model app
├── check_dependencies.py
└── crowd-counter-frontend/
    └── src/
        ├── App.js            # Original app
        ├── App_multimodel.js # Multi-model app
        └── App_multimodel.css
```

---

## 🎓 Training Your Own Models

### CSRNet Training

```python
from models.csrnet import CSRNet
import torch

# Create model
model = CSRNet()

# Train model
# ... your training code ...

# Save checkpoint
torch.save({
    'state_dict': model.state_dict(),
    'optimizer': optimizer.state_dict(),
    'epoch': epoch
}, './checkpoints/csrnet.pth')
```

### YOLOv8 Fine-tuning

```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolov8n.pt')

# Train on your dataset
model.train(
    data='crowd_dataset.yaml',
    epochs=100,
    imgsz=640
)

# Export
model.export(format='pt')
```

---

## 🔗 Additional Resources

- **VMamba Paper**: [Insert link]
- **CSRNet Paper**: https://arxiv.org/abs/1802.10062
- **YOLOv8 Docs**: https://docs.ultralytics.com
- **MCNN Paper**: https://www.cv-foundation.org/openaccess/content_cvpr_2016/papers/Zhang_Single-Image_Crowd_Counting_CVPR_2016_paper.pdf

---

## 💡 Tips

1. **Start with VMamba-TMTB** - It's pre-configured and ready to use
2. **Test YOLOv8 first** - It auto-downloads and is easiest to set up
3. **Use GPU** - Significant performance improvement
4. **Monitor memory** - Switch models if running out of VRAM
5. **Experiment** - Try different models on your specific use case

---

## 📞 Support

If you encounter issues:

1. Check `check_dependencies.py` output
2. Verify all checkpoints are downloaded
3. Ensure correct Python environment is activated
4. Review error logs in terminal

---

**Happy Counting! 🎉**
