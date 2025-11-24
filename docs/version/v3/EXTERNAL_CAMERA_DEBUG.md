# External Camera YOLO Debugging Guide

## 🐛 Issue: "Frame processing failed: 'bbox'"

### Current Status

✅ Fixed `generate_heatmap()` to handle both box formats  
✅ Added safety checks for empty boxes  
✅ Added detailed logging  
✅ Added error handling in backend

### Debugging Steps

#### 1. Check Backend Logs

Start the backend and watch for these log messages:

```bash
cd backend
python run.py
```

**Expected logs when external camera connects:**

```
✅ WebSocket connected for external camera
📹 External camera URL set: http://..., Model: yolo
🔀 Routing external camera to YOLO model
📦 Transforming X boxes from YOLOv8Counter format
✅ Transformed boxes: X boxes in x1,y1,x2,y2 format
📦 Generating YOLO heatmap with X boxes
🎨 Generating heatmap for X boxes
📋 First box format: dict_keys(['x1', 'y1', 'x2', 'y2', 'confidence'])
```

**If you see error:**

```
❌ Error parsing box {...}: 'bbox'
```

This means the box format is still wrong.

#### 2. Test with Different Scenarios

**Scenario A: No people in frame**

- Expected: Should work, return count=0, no heatmap
- Logs should show: "⚠️ No boxes detected, skipping heatmap generation"

**Scenario B: 1 person in frame**

- Expected: count=1, heatmap with 1 box
- Logs should show: "📦 Generating YOLO heatmap with 1 boxes"

**Scenario C: Multiple people**

- Expected: count=N, heatmap with N boxes
- Logs should show: "📦 Generating YOLO heatmap with N boxes"

#### 3. Check Frontend Console

Open browser console (F12) and look for:

```javascript
✅ External camera WebSocket connected
// Should NOT see:
Frame processing failed: 'bbox'
```

#### 4. Verify Backend Code Changes

Make sure these files have the latest changes:

**ml/src/models/yolo/api.py:**

- Line 84: `logger.info(f"📦 Transforming {len(result['boxes'])} boxes...")`
- Line 133: `logger.info(f"🎨 Generating heatmap for {len(boxes)} boxes")`
- Line 141-152: Both `if 'bbox' in box_info` and `else` branches

**backend/app/main.py:**

- Line 320: `logger.info(f"🔀 Routing external camera to {model_type.upper()} model")`
- Line 328-349: Error handling for heatmap generation

#### 5. Manual Test

**Terminal 1 - Backend:**

```bash
cd backend
python run.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm start
```

**Browser:**

1. Go to http://localhost:3000
2. Click "📹 External Camera"
3. Enter camera URL (or use test URL)
4. Select "YOLO" from dropdown
5. Click "Start Stream"
6. Watch backend terminal for logs

#### 6. Test URL Options

**Option A: DroidCam/IP Webcam**

```
http://192.168.1.XXX:8080/video
```

**Option B: Local test image**

```
http://localhost:8000/api/test-image
```

**Option C: Public test stream**

```
http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
```

### Common Issues & Solutions

#### Issue 1: Still getting 'bbox' error

**Solution:**

1. Restart backend server (Ctrl+C, then `python run.py`)
2. Clear browser cache (Ctrl+Shift+R)
3. Check logs for "📦 Transforming" message
4. If not appearing, boxes aren't being transformed

#### Issue 2: No heatmap shown

**Solution:**

1. Check if YOLO is actually detecting people
2. Look for "⚠️ No boxes detected" in logs
3. Try with clearer image/better lighting
4. Switch to different YOLO model (not available in external cam yet)

#### Issue 3: Connection errors

**Solution:**

1. Verify camera URL is accessible
2. Click "Test Camera" button first
3. Check firewall settings
4. Try different camera source

### Code Changes Summary

**Files Modified:**

1. `ml/src/models/yolo/api.py`

   - Added logging to `predict()` function
   - Added safety check in `generate_heatmap()`
   - Added try-catch for box parsing
   - Returns original image if no boxes

2. `backend/app/main.py`

   - Added logging before routing
   - Added error handling for heatmap generation
   - Added check for empty boxes before heatmap

3. `backend/app/services/gated_model_router.py`
   - Already correct (passes transformed boxes)

### Expected Behavior

**With YOLO model:**

```
1. Connect to external camera
2. Send camera URL + model="yolo"
3. Backend receives frame
4. YOLOv8 detects people
5. YOLOv8Counter returns {bbox: [...]} format
6. api.predict() transforms to {x1, y1, x2, y2} format
7. Router receives transformed boxes
8. Router calls generate_heatmap() with transformed boxes
9. generate_heatmap() checks format:
   - If has 'bbox' key → use bbox format
   - Else → use x1,y1,x2,y2 format
10. Heatmap generated successfully
11. Sent to frontend
```

### Verification Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to WebSocket
- [ ] Camera URL accepted
- [ ] Model set to "yolo"
- [ ] Logs show "🔀 Routing external camera to YOLO model"
- [ ] Logs show "📦 Transforming X boxes..."
- [ ] Logs show "✅ Transformed boxes..."
- [ ] Logs show "📦 Generating YOLO heatmap..."
- [ ] Logs show "🎨 Generating heatmap for X boxes"
- [ ] Logs show "📋 First box format: dict_keys([...])"
- [ ] No 'bbox' KeyError in logs
- [ ] Frontend shows count
- [ ] Frontend shows frame
- [ ] Heatmap appears (if visualization enabled)

### If Still Failing

**Collect this information:**

1. **Backend logs:**

   - Copy full error traceback
   - Note which log messages appear
   - Note which are missing

2. **Frontend console:**

   - Copy error messages
   - Check network tab for WebSocket messages

3. **Code version:**

   - Run: `git log -1 --oneline`
   - Check if recent changes are applied

4. **Test data:**
   - Camera URL used
   - Model selected
   - Number of people in frame

### Recovery Steps

**If everything fails, do a clean restart:**

```bash
# Stop all processes
# Ctrl+C in all terminals

# Backend
cd backend
rm -rf __pycache__
rm -rf app/__pycache__
python run.py

# Frontend (new terminal)
cd frontend
npm start

# Browser
# Hard refresh: Ctrl+Shift+R
```

---

**Last Updated:** November 11, 2025  
**Status:** Debugging tools added, ready for testing
