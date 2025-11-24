# 🧪 Webcam YOLO Heatmap - Testing Guide

## Quick Test Plan (5 Minutes)

### Step 1: Start Services

```bash
# Terminal 1 - Backend
cd backend
python run.py
```

Wait for: `✓ Server started on http://localhost:8000`

```bash
# Terminal 2 - Frontend
cd frontend
npm start
```

Wait for: `Compiled successfully!` and browser opens

---

### Step 2: Basic Heatmap Test

**Navigate:**

1. Open `http://localhost:3000`
2. Click **"🎥 Live Webcam"** tab

**Configure:**

- Model: **🚀 YOLOv8 Nano (Fastest)**
- ☑ **Show Detection Overlay** ← CHECK THIS
- ☐ Enable Tracking (Phase 2) ← Leave unchecked for now

**Test:**

1. Click **"🎬 Start Streaming"**
2. Allow webcam access

**Expected Results:**

```
✅ Video feed appears at top
✅ Live count overlay on video (e.g., "Count: 1")
✅ Heatmap image appears below video
✅ Red bounding boxes on heatmap
✅ Confidence scores on boxes (e.g., "0.95")
✅ Stats panel shows:
   - Detected Count: 1
   - Frames Processed: increasing
   - Processing FPS: ~40-60 (CPU)
   - 📦 Detection Boxes section:
     * Total Boxes: 1
     * Avg Confidence: 85.0%
     * Min Confidence: 85.0%
     * Max Confidence: 85.0%
```

**Screenshot Checklist:**

- [ ] Video feed showing you
- [ ] Heatmap with red box around you
- [ ] Confidence score visible on box
- [ ] Stats panel showing metrics

---

### Step 3: Model Comparison Test

**Test each model while streaming:**

**YOLOv8 Nano:**

- Stop streaming
- Select: **🚀 YOLOv8 Nano (Fastest)**
- Start streaming
- Note FPS: **\_\_\_\_** (Expected: 40-60 CPU)

**YOLOv8 Small:**

- Stop streaming
- Select: **⚡ YOLOv8 Small (Fast)**
- Start streaming
- Note FPS: **\_\_\_\_** (Expected: 30-45 CPU)

**YOLOv8 Medium:**

- Stop streaming
- Select: **🎯 YOLOv8 Medium (Balanced)**
- Start streaming
- Note FPS: **\_\_\_\_** (Expected: 20-30 CPU)

**Observations:**

```
Model Size vs FPS:
Nano:   ___ FPS | Inference: ___ ms
Small:  ___ FPS | Inference: ___ ms
Medium: ___ FPS | Inference: ___ ms

✅ Nano should be fastest
✅ Medium should be most accurate
✅ All should detect you
```

---

### Step 4: Heatmap Toggle Test

**Without Heatmap:**

1. Stop streaming
2. ☐ **Uncheck "Show Detection Overlay"**
3. Start streaming

**Expected:**

```
✅ Video feed shows
✅ Count updates
✅ Stats panel shows
❌ No heatmap section below
✅ FPS should be higher (~10-20% faster)
```

**With Heatmap:**

1. Stop streaming
2. ☑ **Check "Show Detection Overlay"**
3. Start streaming

**Expected:**

```
✅ Video feed shows
✅ Count updates
✅ Stats panel shows
✅ Heatmap section appears
✅ Bounding boxes visible
✅ FPS slightly lower (heatmap overhead)
```

---

### Step 5: Multi-Person Test

**Setup:**

1. Use YOLOv8 Nano
2. Enable heatmap
3. Start streaming

**Test Scenarios:**

**Scenario A: Multiple People**

- Have 2-3 people in frame
- Expected:
  ```
  ✅ Count: 3
  ✅ Total Boxes: 3
  ✅ 3 red boxes on heatmap
  ✅ Each box has confidence score
  ✅ Avg Confidence calculated
  ```

**Scenario B: Person Enters/Exits**

- Start with 1 person
- Another person enters frame
- Expected:
  ```
  ✅ Count changes: 1 → 2
  ✅ Total Boxes updates
  ✅ New box appears on heatmap
  ✅ Stats recalculate
  ```

**Scenario C: Partial Occlusion**

- Half-hide behind object
- Expected:
  ```
  ✅ Still detected (if >50% visible)
  ✅ Lower confidence score
  ✅ Box still drawn
  ✅ Min Confidence drops
  ```

---

### Step 6: Tracking Integration Test

**Configure:**

- Model: YOLOv8 Nano
- ☑ Show Detection Overlay
- ☑ **Enable Tracking (Phase 2)** ← Now check this
- Start streaming

**Expected Results:**

```
✅ Count: 1 (current detections)
✅ Unique Tracks: 1 (tracked over time)
✅ 📦 Detection Boxes section shows
✅ ⚡ Phase 2: Speed Analytics section shows:
   - Avg Speed: XX.XX px/s
   - Max Speed: XX.XX px/s
   - Stationary: 1
   - Slow: 0
   - Medium: 0
   - Fast: 0
```

**Movement Test:**

1. Stand still for 3 seconds
   - Expected: Stationary: 1
2. Walk slowly across frame
   - Expected: Slow: 1, Avg Speed increases
3. Walk quickly
   - Expected: Medium or Fast: 1, Max Speed increases

---

### Step 7: Statistics Validation

**Confidence Stats Test:**

Position yourself clearly → Check stats:

```
Total Boxes: 1
Avg Confidence: ~90%
Min Confidence: ~90%
Max Confidence: ~90%
```

Add another person (2 people) → Check stats:

```
Total Boxes: 2
Avg Confidence: ~85-95%
Min Confidence: ~80-90% (partially occluded)
Max Confidence: ~90-95% (clearly visible)
```

**Math Check:**

```
Box 1: 0.92 confidence
Box 2: 0.88 confidence

Expected Avg: (0.92 + 0.88) / 2 = 0.90 = 90%
Actual Avg: ______%

✅ Should match!
```

---

### Step 8: Performance Test

**Measure FPS stability:**

**Test Duration: 30 seconds**

Start streaming with YOLOv8 Nano + Heatmap:

```
Initial FPS: ______
After 10s:   ______
After 20s:   ______
After 30s:   ______

✅ FPS should stay stable (variance <20%)
✅ No memory leaks (check Task Manager)
✅ No WebSocket disconnections
```

**Inference Time Check:**

```
Model: Nano
Min Inference: ______ ms
Avg Inference: ______ ms
Max Inference: ______ ms

✅ CPU: Should be 5-15ms
✅ GPU: Should be 2-5ms
```

---

### Step 9: Error Handling Test

**Test A: Disable Webcam**

1. Start streaming
2. Cover webcam or disable in OS
3. Expected: Error message appears

**Test B: Network Disconnect**

1. Start streaming
2. Stop backend (Ctrl+C in terminal)
3. Expected: Connection error, graceful stop

**Test C: Invalid State**

1. Try changing model while streaming
2. Expected: Dropdown disabled

**Test D: Rapid Toggle**

1. Rapidly enable/disable heatmap
2. Start → Stop → Start quickly
3. Expected: No crashes, state resets correctly

---

### Step 10: Visual Quality Check

**Heatmap Image Quality:**

Check the heatmap image for:

- [ ] Sharp bounding boxes (not blurry)
- [ ] Readable confidence text
- [ ] Correct colors (red boxes)
- [ ] No artifacts or noise
- [ ] Proper aspect ratio (not stretched)
- [ ] Resolution matches webcam (typically 640x480)

**UI Quality:**

- [ ] Smooth animations
- [ ] No layout shifts
- [ ] Responsive design
- [ ] Professional appearance
- [ ] Clear typography
- [ ] Proper spacing

---

## 🎯 Test Results Template

Copy this to your notes:

```
=== WEBCAM YOLO HEATMAP TEST RESULTS ===

Date: _______________
Tester: _____________
System: _____________ (CPU/GPU model)

✅ PASS / ❌ FAIL

[ ] Basic heatmap display
[ ] Bounding boxes visible
[ ] Confidence scores shown
[ ] Stats panel accurate
[ ] Nano model works
[ ] Small model works
[ ] Medium model works
[ ] Large model works
[ ] XLarge model works
[ ] Heatmap toggle works
[ ] Multi-person detection
[ ] Tracking integration
[ ] Performance stable
[ ] Error handling graceful
[ ] Visual quality good

FPS Results:
- Nano: _____ FPS
- Small: _____ FPS
- Medium: _____ FPS

Issues Found:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

Overall: ✅ PASS / ❌ FAIL
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Heatmap not showing

**Symptoms:**

- Video works
- Count updates
- No heatmap image

**Debug Steps:**

```javascript
// Browser Console (F12)
console.log(heatmapImage); // Should show "data:image/jpeg;base64,..."
```

**Solutions:**

1. Check "Show Detection Overlay" is enabled
2. Verify YOLO model selected (not CSRNet)
3. Check backend logs for errors
4. Refresh browser (Ctrl+Shift+R)

---

### Issue 2: Boxes not visible

**Symptoms:**

- Heatmap shows
- No red boxes
- Count is >0

**Debug Steps:**

- Check lighting (ensure room is well-lit)
- Move closer to camera
- Try different background

**Solutions:**

1. Increase room brightness
2. Ensure person is >50% in frame
3. Wear contrasting colors vs background
4. Try different YOLO model (Medium better accuracy)

---

### Issue 3: Low FPS (<10)

**Symptoms:**

- Video laggy
- Heatmap updates slowly
- FPS below 10

**Solutions:**

1. Switch to YOLOv8 Nano
2. Disable heatmap temporarily
3. Disable tracking
4. Close other applications
5. Lower webcam resolution in browser settings

---

### Issue 4: Confidence always 100%

**Symptoms:**

- All boxes show 1.00 or 100%
- Avg = Min = Max

**Debug:**

- This is normal for very clear detections
- Try partial occlusion to see variance

---

### Issue 5: WebSocket error

**Symptoms:**

- "Connection failed"
- No streaming starts

**Solutions:**

1. Check backend running: `http://localhost:8000/docs`
2. Restart backend
3. Clear browser cache
4. Check firewall settings

---

## 📊 Expected Performance

### CPU (Intel i7-10700K)

```
Model    | FPS  | Inference | Accuracy
---------|------|-----------|----------
Nano     | 50   | 6ms       | Good
Small    | 35   | 10ms      | Better
Medium   | 22   | 18ms      | Great
Large    | 15   | 28ms      | Excellent
XLarge   | 10   | 45ms      | Best
```

### GPU (RTX 3060)

```
Model    | FPS  | Inference | Accuracy
---------|------|-----------|----------
Nano     | 120  | 2ms       | Good
Small    | 80   | 4ms       | Better
Medium   | 50   | 7ms       | Great
Large    | 30   | 12ms      | Excellent
XLarge   | 20   | 20ms      | Best
```

---

## ✅ Success Criteria

**All these should work:**

1. ✅ Heatmap displays below video
2. ✅ Red bounding boxes visible
3. ✅ Confidence scores readable
4. ✅ Stats panel shows all metrics
5. ✅ All 5 YOLO models work
6. ✅ Toggle heatmap on/off
7. ✅ Multi-person detection accurate
8. ✅ Tracking integration works
9. ✅ FPS stable >10 (CPU) or >30 (GPU)
10. ✅ No crashes or errors

**If ALL pass → Feature ready for production!** 🚀

---

## 📝 Next Steps After Testing

### If tests pass:

1. Document any performance numbers
2. Take screenshots for documentation
3. Update user guides
4. Prepare demo presentation
5. Deploy to production

### If tests fail:

1. Note exact error messages
2. Check browser console (F12)
3. Check backend logs
4. Report issue with reproduction steps
5. Provide system specs (CPU/GPU model)

---

**Good luck with testing! 🎉**

Remember: The system is designed to work even on modest hardware. If you encounter issues, start with YOLOv8 Nano and gradually test larger models.
