# 🧠 Real-Time Webcam Crowd Counter with VMamba-TMTB

A comprehensive crowd counting system with **two modes**: Image Upload and Real-Time Webcam streaming, powered by VMamba-TMTB (Visual Mamba with Temporal-Multi-Task-Branch) model.

## 🌟 Features

### 📤 Image Upload Mode

- Upload images for crowd counting analysis
- Drag & drop support
- Detailed density map visualization
- Processing time breakdown
- Image preprocessing and postprocessing

### 🎥 Real-Time Webcam Mode (NEW!)

- **Live video streaming** from your webcam
- **Real-time crowd counting** with WebSocket connection
- **FPS monitoring** and performance metrics
- Visual overlay with count display
- Instant feedback on crowd density

---

## 🏗️ Architecture

```
┌─────────────────┐       WebSocket        ┌──────────────────┐
│                 │◄──────────────────────►│                  │
│  React Frontend │     (Real-time)        │  FastAPI Backend │
│  (Port 3000)    │                        │  (Port 8000)     │
│                 │       HTTP POST        │                  │
│                 │◄──────────────────────►│                  │
└─────────────────┘    (Image Upload)      └──────────────────┘
                                                    │
                                                    ▼
                                            ┌──────────────────┐
                                            │  VMamba-TMTB     │
                                            │  Model Inference │
                                            │  (GPU/CPU)       │
                                            └──────────────────┘
```

---

## 📋 Prerequisites

### Required Software

- **Python 3.8+** with pip
- **Node.js 14+** with npm
- **Webcam** (for real-time mode)
- **CUDA-compatible GPU** (optional, for faster inference)

### Python Dependencies

```bash
pip install torch torchvision
pip install fastapi uvicorn
pip install python-multipart
pip install opencv-python
pip install pillow numpy
pip install websockets
```

### Frontend Dependencies

```bash
cd crowd-counter-frontend
npm install
```

---

## 🚀 Quick Start

### Option 1: Using Batch Scripts (Windows)

#### For Real-Time Webcam Mode:

```bash
start_webcam_app.bat
```

#### For Image Upload Mode:

```bash
start_upload_app.bat
```

These scripts will:

1. ✅ Check Python and Node.js installation
2. 🚀 Start the backend server
3. 🌐 Start the frontend server
4. 🎉 Open your browser automatically

---

### Option 2: Manual Setup

#### Step 1: Start Backend (Webcam Mode)

```bash
python webcam_app.py
```

#### Step 1 (Alternative): Start Backend (Upload Mode)

```bash
python fastapi_app.py
```

#### Step 2: Start Frontend

```bash
cd crowd-counter-frontend
npm start
```

#### Step 3: Access Application

Open your browser and navigate to:

```
http://localhost:3000
```

---

## 🎮 How to Use

### 🎥 Real-Time Webcam Mode

1. **Select Webcam Mode**

   - Click the "🎥 Live Webcam" button in the header

2. **Start Streaming**

   - Click "🎬 Start Streaming"
   - Grant webcam permission when prompted

3. **View Real-Time Results**

   - Watch the live video feed with overlay
   - See crowd count updated in real-time
   - Monitor FPS and processing metrics

4. **Stop Streaming**
   - Click "⏹️ Stop Streaming" when done

### 📤 Image Upload Mode

1. **Select Upload Mode**

   - Click the "📤 Upload Image" button in the header

2. **Upload Image**

   - Drag & drop an image, or click to browse
   - Supported formats: JPEG, PNG, BMP, TIFF
   - Max file size: 10 MB

3. **Count Crowd**

   - Click "🧮 Count Crowd" button
   - Wait for processing (usually < 1 second)

4. **View Results**
   - See detected crowd count
   - Review processing breakdown
   - Analyze density map statistics

---

## 📁 Project Structure

```
Major Project/
│
├── webcam_app.py                 # WebSocket backend for real-time streaming
├── fastapi_app.py               # HTTP backend for image upload
├── start_webcam_app.bat         # Launcher for webcam mode
├── start_upload_app.bat         # Launcher for upload mode
│
├── models/
│   ├── vmamba_official.py       # Model loader
│   └── official/                # Official VMamba implementation
│       ├── model.py
│       ├── vmamba.py
│       └── counting_head.py
│
├── utils/
│   ├── preprocess.py            # Image preprocessing
│   ├── postprocess.py           # Count extraction
│   ├── webcam.py                # Webcam utilities (NEW!)
│   └── visualize.py             # Visualization tools
│
├── checkpoints/
│   └── jhu_5.pth               # Pre-trained model weights
│
└── crowd-counter-frontend/
    ├── src/
    │   ├── App.js              # Main app with mode switching
    │   ├── App.css             # Main styles
    │   ├── WebcamCounter.js    # Webcam component (NEW!)
    │   └── WebcamCounter.css   # Webcam styles (NEW!)
    ├── public/
    └── package.json
```

---

## 🔧 Configuration

### Backend Settings

#### Webcam Mode (`webcam_app.py`)

- **WebSocket endpoint**: `ws://localhost:8000/ws/count`
- **Frame rate**: ~10 FPS (configurable)
- **JPEG quality**: 0.8 (configurable)

#### Upload Mode (`fastapi_app.py`)

- **HTTP endpoint**: `http://localhost:8000/count`
- **Max file size**: 10 MB
- **Supported formats**: JPEG, PNG, BMP, TIFF

### Frontend Settings

- **Port**: 3000
- **API URL**: http://localhost:8000
- **WebSocket URL**: ws://localhost:8000/ws/count

---

## 🎯 Performance Optimization

### For Better FPS in Webcam Mode:

1. **Use GPU**

   - Install CUDA and cuDNN
   - PyTorch will automatically use GPU

2. **Reduce Resolution**

   - Lower webcam resolution (e.g., 640x480 instead of 1920x1080)
   - Edit in `WebcamCounter.js`:
     ```javascript
     video: { width: 640, height: 480 }
     ```

3. **Adjust Frame Rate**

   - Increase interval between frames (trade-off: lower FPS)
   - Edit in `WebcamCounter.js`:
     ```javascript
     intervalRef.current = setInterval(captureAndSendFrame, 200); // 5 FPS
     ```

4. **Model Optimization**
   - Use mixed precision (FP16)
   - Model quantization
   - TensorRT optimization

---

## 🐛 Troubleshooting

### Webcam Not Working

- ✅ Check browser permissions
- ✅ Ensure webcam is not in use by another application
- ✅ Try different browsers (Chrome/Edge recommended)

### WebSocket Connection Failed

- ✅ Verify backend server is running on port 8000
- ✅ Check firewall settings
- ✅ Review browser console for errors

### Slow Performance

- ✅ Close other applications
- ✅ Use GPU if available
- ✅ Reduce video resolution
- ✅ Decrease frame rate

### Model Not Loading

- ✅ Verify checkpoint file exists: `checkpoints/jhu_5.pth`
- ✅ Check model path in code
- ✅ Ensure PyTorch is installed correctly

---

## 📊 Technical Details

### Model

- **Architecture**: VMamba-TMTB (Visual Mamba with Temporal-Multi-Task-Branch)
- **Input**: RGB images (any size)
- **Output**: Density map for crowd counting
- **Preprocessing**: Normalization with ImageNet statistics
- **Postprocessing**: Sum of density map with calibration

### WebSocket Protocol

```json
// Client -> Server
{
  "frame": "data:image/jpeg;base64,..."
}

// Server -> Client
{
  "success": true,
  "count": 42,
  "fps": 8.5,
  "frame_number": 150,
  "timing": {
    "preprocess_ms": 5.2,
    "inference_ms": 85.3,
    "postprocess_ms": 2.1,
    "total_ms": 92.6
  },
  "reasoning": "Medium activation pattern...",
  "density_map_stats": {
    "min": 0.0,
    "max": 0.0543,
    "mean": 0.0012,
    "sum": 42.3
  }
}
```

---

## 🎨 UI Features

### Webcam Mode UI

- ✨ Live video preview
- 📊 Real-time count overlay
- 📈 FPS monitoring
- ⏱️ Processing time breakdown
- 🧠 Model reasoning display
- 📉 Density map statistics

### Upload Mode UI

- 📤 Drag & drop upload
- 🖼️ Image preview
- 📊 Detailed results panel
- ⏱️ Processing breakdown
- 🔥 Heatmap visualization (if enabled)

---

## 🔜 Future Enhancements

- [ ] Multi-camera support
- [ ] Video file processing
- [ ] Recording and playback
- [ ] Historical data tracking
- [ ] Alert system for crowd threshold
- [ ] Export results to CSV/JSON
- [ ] Heatmap overlay on live video
- [ ] Zone-based counting
- [ ] People tracking and flow analysis

---

## 📝 License

This project is for educational purposes. Model weights and architecture are based on official VMamba-TMTB implementation.

---

## 🙏 Acknowledgments

- VMamba-TMTB model architecture
- FastAPI framework
- React framework
- OpenCV for video processing

---

## 📧 Contact

For questions or issues, please contact the development team.

---

## 🚀 Getting Started Checklist

- [ ] Install Python 3.8+
- [ ] Install Node.js 14+
- [ ] Install Python dependencies
- [ ] Install frontend dependencies
- [ ] Download model checkpoint to `checkpoints/jhu_5.pth`
- [ ] Run `start_webcam_app.bat` or `start_upload_app.bat`
- [ ] Open browser to http://localhost:3000
- [ ] Grant webcam permissions (for webcam mode)
- [ ] Start counting! 🎉

---

**Happy Counting! 🎊**
