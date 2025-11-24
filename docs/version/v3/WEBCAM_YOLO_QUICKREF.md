# 🎯 Webcam YOLO + Heatmap - Quick Reference

## ⚡ 30-Second Test

```bash
# Terminal 1
cd backend && python run.py

# Terminal 2
cd frontend && npm start

# Browser
http://localhost:3000
→ 🎥 Live Webcam
→ Model: 🚀 YOLOv8 Nano
→ ☑ Show Detection Overlay
→ 🎬 Start Streaming
```

**Expected:** Video + Heatmap with red boxes + Stats panel

---

## 🎛️ UI Controls

### Model Selection

```
🚀 YOLOv8 Nano (Fastest)     - CPU, 50+ FPS
⚡ YOLOv8 Small (Fast)        - CPU, 35+ FPS
🎯 YOLOv8 Medium (Balanced)   - GPU, 25+ FPS
🔥 YOLOv8 Large (Accurate)    - GPU, 15+ FPS
💎 YOLOv8 XLarge (Best)       - GPU, 10+ FPS
```

### Toggles

- ☑ **Show Detection Overlay** - Enable heatmap
- ☑ **Enable Tracking (Phase 2)** - Speed analytics

### Buttons

- 🎬 **Start Streaming** - Begin webcam capture
- ⏹️ **Stop Streaming** - End session

---

## 📊 Statistics Display

### Live Results Panel

```
Detected Count: 2          ← Current frame detections
Unique Tracks: 2           ← If tracking enabled
Frames Processed: 450      ← Total frames analyzed
Processing FPS: 42.15      ← Real-time performance
Inference Time: 8.2 ms     ← Model inference
Total Time: 15.7 ms        ← End-to-end
```

### Detection Boxes (YOLO only)

```
Total Boxes: 2             ← Number of detections
Avg Confidence: 89.5%      ← Mean confidence
Min Confidence: 85.0%      ← Lowest score
Max Confidence: 94.0%      ← Highest score
```

### Speed Analytics (If tracking enabled)

```
Avg Speed: 45.3 px/s       ← Mean movement
Max Speed: 89.1 px/s       ← Fastest detected
Stationary: 1              ← Not moving
Slow: 1                    ← Slow movement
Medium: 0                  ← Medium speed
Fast: 0                    ← Fast movement
```

---

## 🔥 Heatmap Display

```
🔥 Detection Overlay
┌────────────────────────────────┐
│                                │
│   ┌──────────┐                 │
│   │  Person  │ 0.95            │
│   │          │                 │
│   └──────────┘                 │
│                  ┌──────────┐  │
│                  │  Person  │  │
│                  │          │  │
│                  └──────────┘  │
│                      0.87       │
└────────────────────────────────┘

💡 Bounding boxes show detected people with confidence scores
```

**Features:**

- Red bounding boxes
- Confidence scores (0-1 scale)
- Real-time updates (~100ms)
- Synchronized with video
- Toggle on/off

---

## 🌐 WebSocket API

### Request Format

```json
{
  "frame": "data:image/jpeg;base64,/9j/...",
  "model": "yolo-nano",
  "tracking": false,
  "heatmap": true
}
```

### Response Format

```json
{
  "success": true,
  "count": 2,
  "boxes": [{ "x1": 100, "y1": 150, "x2": 200, "y2": 350, "confidence": 0.95 }],
  "confidence_stats": {
    "avg": 0.91,
    "min": 0.87,
    "max": 0.95
  },
  "heatmap": "data:image/jpeg;base64,/9j/...",
  "timing": {
    "inference_ms": 8.2,
    "total_ms": 15.7
  }
}
```

---

## 🐛 Quick Troubleshooting

### No heatmap showing

✓ Check "Show Detection Overlay" enabled  
✓ Verify YOLO model selected  
✓ Check backend logs for errors

### Low FPS (<10)

✓ Switch to YOLOv8 Nano  
✓ Disable heatmap temporarily  
✓ Close other applications

### Boxes not visible

✓ Increase room brightness  
✓ Move closer to camera  
✓ Ensure person >50% in frame

### WebSocket error

✓ Check backend running on port 8000  
✓ Restart backend and frontend  
✓ Check firewall settings

---

## 📈 Performance Targets

### CPU (Intel i7)

| Model  | FPS | Inference |
| ------ | --- | --------- |
| Nano   | 50  | 6ms       |
| Small  | 35  | 10ms      |
| Medium | 22  | 18ms      |

### GPU (RTX 3060)

| Model  | FPS | Inference |
| ------ | --- | --------- |
| Nano   | 120 | 2ms       |
| Small  | 80  | 4ms       |
| Medium | 50  | 7ms       |

**Heatmap Overhead:** +8-14ms

---

## ✅ Test Checklist

Quick validation:

- [ ] Backend starts without errors
- [ ] Frontend loads successfully
- [ ] Webcam permission granted
- [ ] Video feed displays
- [ ] Can select YOLO models
- [ ] Heatmap toggle works
- [ ] Heatmap shows below video
- [ ] Bounding boxes visible
- [ ] Confidence scores shown
- [ ] Stats panel displays
- [ ] FPS >10 (CPU) or >30 (GPU)
- [ ] No console errors

---

## 🎓 Key Files

### Frontend

- `frontend/src/WebcamCounter.js` - Main component
- `frontend/src/WebcamCounter.css` - Styles

### Backend

- `backend/app/main.py` - WebSocket endpoint

### Documentation

- `docs/version/v3/WEBCAM_YOLO_HEATMAP.md` - Full guide
- `docs/version/v3/WEBCAM_YOLO_TESTING.md` - Test plan
- `docs/version/v3/WEBCAM_YOLO_COMPLETE_STATUS.md` - Status

---

## 🚀 Usage Tips

### Best Performance

1. Use YOLOv8 Nano on CPU
2. Use YOLOv8 Medium+ on GPU
3. Disable heatmap if lag occurs
4. Close other applications
5. Ensure good lighting

### Best Accuracy

1. Use YOLOv8 Large or XLarge
2. Enable heatmap to verify detections
3. Ensure people fully in frame
4. Use tracking for counting over time

### Best Demo

1. Use YOLOv8 Small (balanced)
2. Enable heatmap for visual appeal
3. Enable tracking for analytics
4. Test with 2-3 people
5. Show statistics panel

---

## 📞 Support

**Issue with code?**

1. Check browser console (F12)
2. Check backend terminal logs
3. Review error messages
4. Check `docs/version/v3/WEBCAM_YOLO_TESTING.md`

**Performance issues?**

1. Switch to Nano model
2. Disable heatmap/tracking
3. Check system resources
4. Review performance benchmarks

**Questions?**

- See `docs/version/v3/WEBCAM_YOLO_HEATMAP.md` for details
- Check troubleshooting guide in testing doc

---

**Status:** ✅ READY FOR TESTING  
**Last Updated:** January 2025

🎯 **Next Step:** Start backend & frontend, test webcam YOLO!
