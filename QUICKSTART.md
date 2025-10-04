# 🚀 Quick Start Guide - Real-Time Webcam Crowd Counter

## ⚡ 30-Second Setup

### Windows Users:

1. Double-click `start_webcam_app.bat`
2. Wait for servers to start (~10 seconds)
3. Browser opens automatically at http://localhost:3000
4. Click "🎥 Live Webcam" → "🎬 Start Streaming"
5. Done! 🎉

---

## 📋 Prerequisites Check

```bash
# Check Python
python --version
# Should show: Python 3.8 or higher

# Check Node.js
node --version
# Should show: v14.0 or higher

# Check pip
pip --version
```

---

## 🔧 First Time Setup

### 1. Install Python Dependencies

```bash
pip install torch torchvision fastapi uvicorn python-multipart opencv-python pillow numpy websockets
```

### 2. Install Frontend Dependencies

```bash
cd crowd-counter-frontend
npm install
```

### 3. Verify Model Checkpoint

- Ensure `checkpoints/jhu_5.pth` exists
- Size should be ~100-200 MB

---

## 🎮 Usage

### Mode 1: Real-Time Webcam 🎥

```bash
# Start servers
start_webcam_app.bat

# In browser (http://localhost:3000):
1. Click "🎥 Live Webcam"
2. Click "🎬 Start Streaming"
3. Allow webcam access
4. See real-time crowd count!
```

### Mode 2: Image Upload 📤

```bash
# Start servers
start_upload_app.bat

# In browser (http://localhost:3000):
1. Click "📤 Upload Image"
2. Drag & drop image or click to browse
3. Click "🧮 Count Crowd"
4. View results!
```

---

## 🏃 Manual Start (If batch files don't work)

### Terminal 1 - Backend:

```bash
python webcam_app.py
# Wait for: "✅ VMamba-TMTB model loaded successfully"
```

### Terminal 2 - Frontend:

```bash
cd crowd-counter-frontend
npm start
# Opens browser automatically
```

---

## 🔍 Verify Everything Works

### Check Backend Health:

```bash
# Open in browser:
http://localhost:8000/health

# Should return:
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda" or "cpu"
}
```

### Check Frontend:

```bash
# Open in browser:
http://localhost:3000

# Should see:
- Header with "VMamba-TMTB Crowd Counter"
- Two mode buttons
- Upload interface or webcam view
```

---

## ⚠️ Common Issues & Fixes

### Issue: "Model not loaded"

**Fix:**

```bash
# Verify checkpoint path
dir checkpoints\jhu_5.pth

# If missing, download or copy checkpoint file
```

### Issue: "Webcam not accessible"

**Fix:**

1. Close other apps using webcam (Zoom, Teams, etc.)
2. Allow webcam permissions in browser
3. Try different browser (Chrome recommended)
4. Restart browser

### Issue: "Port 8000 already in use"

**Fix:**

```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Then restart backend
```

### Issue: "Port 3000 already in use"

**Fix:**

```bash
# Kill Node.js processes
taskkill /IM node.exe /F

# Then restart frontend
```

### Issue: "Slow performance / Low FPS"

**Fix:**

1. Close other applications
2. Use GPU (install CUDA if available)
3. Reduce webcam resolution (edit WebcamCounter.js)
4. Increase frame interval (lower FPS but faster processing)

---

## 🎯 Performance Tips

### For Best Real-Time Performance:

**GPU Users (CUDA):**

```bash
# Check if GPU is being used
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

**Optimize Settings:**

```javascript
// In WebcamCounter.js
// Lower resolution = faster processing
video: { width: 640, height: 480 }  // Default
video: { width: 320, height: 240 }  // Faster

// Frame interval (ms between captures)
setInterval(captureAndSendFrame, 100)  // 10 FPS (default)
setInterval(captureAndSendFrame, 200)  // 5 FPS (faster)
```

---

## 📊 Expected Performance

### With GPU (NVIDIA):

- FPS: 8-15 FPS
- Inference: 50-100ms per frame
- Total latency: ~100-150ms

### With CPU:

- FPS: 2-5 FPS
- Inference: 200-500ms per frame
- Total latency: ~300-600ms

---

## 🎨 UI Guide

### Webcam Mode Display:

```
┌─────────────────────────────────┐
│  Count: 42          8.5 FPS     │ ← Overlay
│                                 │
│        [Live Video Feed]        │
│                                 │
└─────────────────────────────────┘
           ↓
    📊 Live Results
    • Detected Count: 42
    • Frames Processed: 150
    • Processing FPS: 8.5
    • Inference Time: 85ms
```

---

## 🛑 Shutdown

### Using Batch File:

- Press any key in the batch file window
- Servers will stop automatically

### Manual Shutdown:

```bash
# Press Ctrl+C in each terminal
# Or close terminal windows
```

---

## 📝 Quick Commands Reference

```bash
# Start webcam mode
start_webcam_app.bat

# Start upload mode
start_upload_app.bat

# Check backend status
curl http://localhost:8000/health

# View backend logs
# Check Terminal 1 output

# View frontend logs
# Check Terminal 2 output

# Stop all
# Press any key in batch window
```

---

## 🆘 Need Help?

1. **Check logs**: Look at terminal output for errors
2. **Verify installation**: Run prerequisite checks
3. **Restart everything**: Stop all servers and start again
4. **Check README**: See WEBCAM_README.md for detailed info
5. **Browser console**: Press F12 in browser, check Console tab

---

## ✅ Success Indicators

You'll know it's working when you see:

**Backend:**

```
✅ VMamba-TMTB model loaded successfully
📊 Model parameters: 25,000,000+
🔧 Using device: cuda
```

**Frontend:**

```
Compiled successfully!
Local: http://localhost:3000
```

**Webcam Mode:**

```
✅ WebSocket connected
📹 Processing frames...
Count: [number] | FPS: [number]
```

---

## 🎉 You're Ready!

Now you can:

- ✅ Count crowds in real-time from your webcam
- ✅ Upload images for crowd analysis
- ✅ Monitor processing performance
- ✅ See detailed inference metrics

**Enjoy your crowd counting! 🎊**

---

_For detailed documentation, see: WEBCAM_README.md_
