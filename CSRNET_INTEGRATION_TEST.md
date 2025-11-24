# CSRNet Integration - Testing & Validation Guide

## Quick Integration Test

Run these steps in order to verify CSRNet data flow end-to-end.

---

## Step 1: Backend Health Check ✅

### 1.1 Check CSRNet API is registered

```bash
curl http://localhost:8000/docs
```

**Expected:** Swagger UI shows `/api/v1/csrnet` endpoints

### 1.2 Health endpoint

```bash
curl http://localhost:8000/api/v1/csrnet/health
```

**Expected Response:**

```json
{ "status": "ok", "model": "CSRNet" }
```

### 1.3 Check model is loaded

```bash
# Start backend with verbose logging
python backend/run.py
```

**Expected logs:**

```
INFO: ✅ CSRNet API loaded successfully
INFO: Available models: ['csrnet', 'yolo-nano', 'tmtb']
```

---

## Step 2: Frontend WebSocket Connection ✅

### 2.1 Open browser console

1. Navigate to `http://localhost:3000/webcam` (or `http://localhost:5173/webcam`)
2. Press `F12` to open Developer Tools
3. Go to Console tab

### 2.2 Check for connection message

**Expected log:**

```
✅ WebSocket connected
```

### 2.3 If NOT connected:

- Check backend is running on `localhost:8000`
- Check CORS middleware in `backend/app/main.py` includes your frontend URL
- Check WebSocket URL in `frontend/src/pages/Webcam.js` line 75 is correct

---

## Step 3: Verify Frame Transmission ✅

### 3.1 Monitor Network Tab

1. Open DevTools → Network tab
2. Filter for WebSocket messages (WS filter)
3. Click "Start" button in Settings

**Expected:**

- WebSocket connection should show as "101 Switching Protocols"
- Messages flowing continuously (every 100ms)

### 3.2 Examine WebSocket Message

1. Click on WebSocket connection in Network tab
2. Go to "Messages" subtab
3. Click on outgoing message

**Expected payload:**

```json
{
  "frame": "data:image/jpeg;base64,iVBORw0KG...",
  "model": "csrnet",
  "tracking": false,
  "heatmap": false,
  "threshold": 0.5
}
```

---

## Step 4: Verify Backend Processing ✅

### 4.1 Check backend logs

```
INFO: ✅ WebSocket connected for real-time counting
INFO: Processing frame 1 with model: csrnet
INFO: Prediction successful: count=45, inference_time=125.5ms
```

### 4.2 Monitor inference time

Expected: 120-150ms per frame for CSRNet

---

## Step 5: Verify Frontend Response Reception ✅

### 5.1 Check WebSocket response in Network tab

**Expected response payload:**

```json
{
  "success": true,
  "model": "csrnet",
  "count": 45,
  "inference_time_ms": 125.5,
  "frame_number": 1,
  "fps": 7.9
}
```

### 5.2 Check browser console for errors

**Should NOT see:**

```
❌ WebSocket error
❌ Processing error
```

---

## Step 6: Verify State Updates ✅

### 6.1 Open React DevTools

1. Install React DevTools browser extension
2. Go back to webpage
3. Open DevTools → Components tab

### 6.2 Inspect Webcam component state

1. Click on "Webcam" component
2. Look for "State" section

**Expected values (after start):**

```javascript
isStreaming: true
results: {
  success: true,
  count: 45,
  fps: 7.9,
  inference_time_ms: 125.5,
  frame_number: 1,
  model: "csrnet"
}
fps: 7.9
frameCount: 1
countHistory: [
  {time: 1700700000000, count: 45},
  {time: 1700700000100, count: 46},
  ...
]
heatmapImage: null (or base64 if enabled)
```

---

## Step 7: Verify Visualization Cards ✅

### 7.1 LiveFeedCard

- [ ] Video stream displays
- [ ] Count overlay shows current count (e.g., "45")
- [ ] FPS updates (e.g., "7.9 FPS")
- [ ] Updates smoothly

### 7.2 HeatmapCard

- [ ] If heatmap DISABLED: Shows "Enable Detection Overlay in settings"
- [ ] If heatmap ENABLED: Shows density visualization
- [ ] Updates every frame when enabled

### 7.3 GraphCard

- [ ] Shows "Start streaming to see real-time graph" when not streaming
- [ ] After start: Shows line chart
- [ ] Chart adds new point every frame
- [ ] Statistics show: Data Points, Current, Average, Peak

### 7.4 MetricsCard

- [ ] Shows model: "CSRNet"
- [ ] Shows inference time: "125.5 ms"
- [ ] Shows frame number: "1", "2", "3", ...
- [ ] If tracking enabled: Shows tracking metrics

---

## Step 8: Test Settings Controls ✅

### 8.1 Model Selection

1. Start streaming with "csrnet" selected
2. Verify count displays and updates
3. Change to "yolo-nano"
   - [ ] Backend should switch models
   - [ ] Response should have `"model": "yolo"`
   - [ ] Count may differ (detection vs density)
4. Change back to "csrnet"
   - [ ] Should switch back

### 8.2 Detection Threshold

1. With CSRNet: Threshold doesn't affect count (all detections counted)
2. With YOLO: Should filter by confidence
3. Adjust slider 0.3 → 0.5 → 0.7
   - [ ] Count may decrease with higher threshold

### 8.3 Enable Heatmap

1. [ ] Toggle ON: HeatmapCard should show density visualization
2. [ ] Toggle OFF: Should show placeholder

### 8.4 Enable Tracking (YOLO only)

1. [ ] Select YOLO model
2. [ ] Toggle Tracking ON
3. [ ] Should see trajectory lines overlay on video

### 8.5 Display Options

1. [ ] Toggle each card visibility checkbox
2. [ ] Corresponding card should appear/disappear

---

## Step 9: Test Auto-Switch (if enabled) ✅

### 9.1 Configure Auto-Switch

1. [ ] Enable "Auto-Switch Model"
2. [ ] Set threshold to 30

### 9.2 Test switch logic

```
Count < 30 → Should use YOLO
Count >= 30 → Should use CSRNet (or other density model)
```

1. [ ] Monitor count in MetricsCard
2. [ ] Watch Model field
3. [ ] Should switch when crossing threshold

---

## Step 10: Test Error Handling ✅

### 10.1 Stop backend

1. Stop backend server (Ctrl+C)
2. Leave frontend running and streaming

**Expected:**

- [ ] Error message appears: "Connection lost. Please restart."
- [ ] Can click "Stop" to stop streaming
- [ ] No crashes

### 10.2 Restart backend

1. Restart backend server
2. Click "Start" again on frontend

**Expected:**

- [ ] Reconnects automatically
- [ ] Streaming resumes
- [ ] New count displays

### 10.3 Test with wrong URL

1. Modify WebSocket URL in `Webcam.js` to invalid URL
2. Click "Start"

**Expected:**

- [ ] Error message appears
- [ ] No crash

---

## Step 11: Performance Testing ✅

### 11.1 Monitor FPS

1. Start streaming with CSRNet
2. Watch FPS counter in LiveFeedCard
3. Monitor backend inference time in logs

**Expected:**

```
FPS: 7-10 (frame interval 100ms)
Inference time: 120-150ms per frame
Total latency: 200-250ms
```

### 11.2 Check network bandwidth

1. DevTools → Network tab
2. Filter for WebSocket
3. Note message size

**Expected:**

- Each outgoing frame: ~92KB (base64 encoded)
- Each incoming response: ~1KB (JSON)
- Total: ~93KB per frame (930KB/s at 10 fps)

### 11.3 Check browser memory

1. DevTools → Memory tab
2. Note heap size after 30 seconds of streaming

**Expected:**

- Stable heap (not continuously growing)
- No major spikes
- Should be <100MB for webcam page

---

## Step 12: End-to-End Integration Test ✅

### Complete flow test:

```
1. Start backend
   └─ Verify CSRNet loaded

2. Open frontend → Webcam page
   └─ Verify SettingsSidebar + 4 cards render

3. Select CSRNet model
   └─ Verify selection updates

4. Click "Start"
   └─ Verify:
      • Video plays
      • Count overlay shows number
      • Graph shows points
      • Metrics update

5. Enable Heatmap
   └─ Verify HeatmapCard shows visualization

6. Change model to YOLO
   └─ Verify:
      • Model switches
      • Response changes
      • Count may differ

7. Enable Tracking (YOLO)
   └─ Verify trajectory visible

8. Set Display options
   └─ Verify cards toggle visibility

9. Click "Stop"
   └─ Verify:
      • Video stops
      • Count freezes
      • Graph stops updating

10. Stop backend
    └─ Verify error message appears

11. Restart backend + Click "Start"
    └─ Verify reconnects and resumes
```

---

## Debugging Checklist

### If CSRNet is not working:

| Issue                   | Check                     | Solution                             |
| ----------------------- | ------------------------- | ------------------------------------ |
| No WebSocket connection | Backend running on 8000   | `python backend/run.py`              |
| Connection error        | WebSocket URL correct     | Check `Webcam.js` line 75            |
| CORS error              | Frontend URL in CORS list | Update `backend/app/main.py` origins |
| Model not found         | CSRNet imported correctly | Check `backend/app/main.py` line 47  |
| Model path wrong        | Checkpoint exists         | Check `ml/checkpoints/csrnet.pth`    |
| Inference error         | Check GPU memory          | Monitor with `nvidia-smi`            |
| No count displayed      | Check response structure  | Verify `data.count` exists           |
| Graph not plotting      | countHistory updating     | Check `setCountHistory()` in state   |
| Heatmap not showing     | Backend returning heatmap | Enable in settings, check response   |
| High latency            | Check network/GPU         | Profile inference time               |

---

## Quick Verification Commands

```bash
# 1. Backend running?
curl http://localhost:8000/health

# 2. CSRNet endpoints available?
curl http://localhost:8000/docs | grep csrnet

# 3. Model checkpoint exists?
ls -lh ml/checkpoints/csrnet.pth

# 4. Backend logs showing CSRNet?
grep "CSRNet" backend.log

# 5. Frontend WebSocket connecting?
# (Check browser console for "✅ WebSocket connected")

# 6. Check response format
# (DevTools → Network → WebSocket → Messages)
```

---

## Success Criteria ✅

**All tests pass when:**

- [ ] Backend CSRNet API loads successfully
- [ ] Frontend WebSocket connects to backend
- [ ] Frames are transmitted every 100ms
- [ ] Backend processes frames with CSRNet
- [ ] Responses are sent back with count data
- [ ] Frontend state updates with response data
- [ ] LiveFeedCard displays count overlay
- [ ] GraphCard plots count history
- [ ] HeatmapCard displays heatmap (when enabled)
- [ ] MetricsCard shows timing and model info
- [ ] Settings control all features properly
- [ ] No error messages in console
- [ ] Performance is acceptable (<300ms latency)

**When all criteria met: Integration is complete and working! 🚀**
