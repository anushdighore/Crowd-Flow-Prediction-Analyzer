# External Camera Tracking Debugging Guide

## Issue: No trajectory, speed, or tracking data displayed in ExternalCam

### Changes Made

#### 1. **Frontend Debug Enhancements** (`frontend/src/components/ExternalCam.js`)

**Added comprehensive logging:**

```javascript
// Log all received data
console.log("📦 Received data:", data);

// Log tracking-specific data
if (data.tracks) {
  console.log("🎯 Tracking data received:", data.tracks.length, "tracks");
  console.log("Track details:", data.tracks);
}
```

**Enabled tracking by default:**

```javascript
const [enableTracking, setEnableTracking] = useState(true); // Was false
const [showSettings, setShowSettings] = useState(true); // Was false
```

**Fixed WebSocket dependencies:**

```javascript
// Added missing dependencies
}, [cameraUrl, selectedModel, isStreaming, autoSwitch, currentAutoModel, enableTracking]);
```

**Added debug panel in stats:**

```javascript
<div
  className="stat-item"
  style={{ background: "#fff3cd", borderLeft: "4px solid #ffc107" }}
>
  <span className="stat-label">🐛 Debug Info:</span>
  <span className="stat-value">
    Tracking: {enableTracking ? "✅" : "❌"} | Tracks:{" "}
    {results.tracks ? results.tracks.length : "N/A"} | Unique:{" "}
    {results.unique_count || "N/A"}
  </span>
</div>
```

**Added waiting state for tracks:**

```javascript
{enableTracking && results && (
  <>
    {results.tracks && results.tracks.length > 0 ? (
      // Show track table
    ) : (
      // Show waiting message with troubleshooting tips
    )}
  </>
)}
```

#### 2. **Test Script** (`scripts/test_external_camera_tracking.py`)

Created a comprehensive test script to verify backend tracking functionality.

### Debugging Steps

#### Step 1: Check Browser Console

Open browser DevTools (F12) and look for:

```
📤 Sending connection data: {camera_url: "...", model: "yolo-nano", tracking: true}
✅ External camera WebSocket connected
📦 Received data: {success: true, count: 5, ...}
```

**What to check:**

- Is `tracking: true` being sent?
- Is the response including `tracks` array?
- Are there any error messages?

#### Step 2: Check Debug Info Panel

Look at the yellow debug panel in the stats section:

```
🐛 Debug Info: Tracking: ✅ | Tracks: N/A | Unique: N/A
```

**What this tells you:**

- **Tracking: ✅** = Frontend has tracking enabled
- **Tracks: N/A** = Backend is not sending tracking data
- **Tracks: 0** = Tracking enabled but no objects detected
- **Tracks: 5** = Tracking working! 5 active tracks

#### Step 3: Run Backend Test Script

```bash
cd "d:\College\Major Project"
python scripts\test_external_camera_tracking.py
```

**Update the camera URL in the script first!**

This will show:

- ✅ If WebSocket connects
- 📊 If frames are being processed
- 🎯 If tracking data is present in responses
- ⚡ Speed statistics

**Expected output:**

```
Frame 1:
  ✅ Success
  📊 Count: 5
  🎯 Unique Count: 4
  🎯 Tracks: 4
     Track #1:
       State: 1 (TRACKED)
       Position: [320, 240]
       Speed: 12.5 px/s
       Frames: 8
       Trajectory points: 15
```

#### Step 4: Check Backend Logs

Look for these in the backend console:

```
📹 External camera URL set: http://..., Model: yolo-nano, Tracking: True
✅ Initialized YOLO tracking counter with yolov8n.pt
```

**If you see:**

- `Tracking: False` → Frontend not sending tracking flag
- `Tracking counter not available` → UnifiedCounter initialization failed
- No tracking messages → Backend not receiving tracking parameter

### Common Issues & Solutions

#### Issue 1: No tracking data in response

**Symptoms:**

- Debug panel shows: `Tracks: N/A`
- Console shows data but no `tracks` field

**Solution:**

```python
# In backend/app/main.py, verify this code exists:
if enable_tracking and model_type.lower() in yolo_model_map:
    response_data["unique_count"] = result.get("unique_count", response_data["count"])
    response_data["tracks"] = result.get("tracks", [])
    if "speed_stats" in result:
        response_data["speed_stats"] = result["speed_stats"]
```

#### Issue 2: Tracking enabled but tracks = 0

**Symptoms:**

- Debug panel shows: `Tracks: 0`
- Waiting message displayed

**Possible causes:**

1. **No objects in frame** → Point camera at people
2. **Low confidence** → Objects detected but filtered out
3. **Model not loaded** → Check backend initialization

**Solution:**

- Ensure camera shows people
- Lower detection threshold if needed
- Check backend logs for model loading

#### Issue 3: WebSocket not connecting

**Symptoms:**

- Error: "WebSocket connection error"
- No data received

**Solution:**

1. Check backend is running: `http://localhost:8000/health`
2. Check firewall settings
3. Verify camera URL is accessible

#### Issue 4: Tracks showing but no trajectory paths

**Symptoms:**

- Track table shows data
- No colored lines on video

**Solution:**
Check canvas is rendering:

```javascript
// In drawTrajectories callback
console.log("Drawing trajectories:", results.tracks.length);
console.log("Canvas size:", canvas.width, canvas.height);
```

Canvas needs valid dimensions from image:

```javascript
if (canvas.width !== img.naturalWidth || canvas.height !== img.naturalHeight) {
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
}
```

### Verification Checklist

Before reporting issues, verify:

- [ ] Backend running (`python run.py`)
- [ ] Frontend running (`npm start`)
- [ ] Camera URL accessible (test with browser)
- [ ] YOLO model selected (not CSRNet/TMTB)
- [ ] Settings panel shows tracking enabled (✅)
- [ ] Debug panel shows `Tracking: ✅`
- [ ] Browser console shows connection data sent
- [ ] No errors in browser console
- [ ] No errors in backend console
- [ ] Test script runs successfully

### Expected Console Output (Working)

**Frontend Console:**

```
📤 Sending connection data: {
  camera_url: "http://192.168.137.168:8080/video",
  model: "yolo-nano",
  tracking: true
}
✅ External camera WebSocket connected

📦 Received data: {
  success: true,
  model: "yolo-nano-tracking",
  count: 5,
  raw_count: 5.23,
  unique_count: 4,
  tracks: Array(4),
  speed_stats: {...},
  frame: "data:image/jpeg;base64,...",
  heatmap: "data:image/jpeg;base64,..."
}

🎯 Tracking data received: 4 tracks
Track details: [
  {id: 1, state: 1, position: [320, 240], speed: 12.5, frames_tracked: 8, trajectory: [...]},
  ...
]
```

**Backend Console:**

```
📹 External camera URL set: http://192.168.137.168:8080/video, Model: yolo-nano, Tracking: True
✅ Initialized YOLO tracking counter with yolov8n.pt
📦 Generating YOLO heatmap with 5 boxes
```

### Quick Fix Commands

**Reset everything:**

```bash
# Stop backend (Ctrl+C)
# Stop frontend (Ctrl+C)

# Clear browser cache and reload
# Restart backend
cd backend
python run.py

# Restart frontend
cd frontend
npm start
```

**Force refresh frontend:**

```bash
cd frontend
rm -rf node_modules/.cache
npm start
```

### Contact Info

If issues persist after following this guide:

1. Run test script and save output
2. Check browser console and save logs
3. Check backend console and save logs
4. Report with all three logs included

---

**Last Updated:** 2025-11-11
