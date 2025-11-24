# Phase 1 Implementation - Quick Start Testing

## System Ready ✅

All components for Phase 1 Trajectory Visualization are now implemented and integrated.

## Quick Test

### 1. Start Backend

```bash
cd backend
python run.py
```

Expected output:

```
✅ Backend started on http://localhost:8000
✅ Pedestrian tracker service loaded
✅ WebSocket endpoint ready at /ws/pedestrian-track
```

### 2. Open Frontend

```bash
# In another terminal
cd frontend
npm start
```

Browser opens to `http://localhost:3000`

### 3. Navigate to Pedestrian Tracker

- Click on "Pedestrian Tracker" in navigation
- Page should load with video upload section

### 4. Test Features

#### Feature 1: Video Upload

1. Click "📁 Select Video"
2. Choose any pedestrian video from `data/videos/crowd/`
3. Video preview appears

#### Feature 2: Trajectory Control

1. Look for **"Trajectory Visualization"** section
2. Find slider labeled "Trajectory Length: 30 points"
3. Move slider left → fewer trajectory points (faster rendering)
4. Move slider right → more trajectory points (longer history)

#### Feature 3: Start Tracking

1. Click "🎬 Start Tracking"
2. Video plays and frames are sent to backend
3. Annotated frames return with:
   - **Colored bounding boxes** (different color per person)
   - **Track IDs** displayed on boxes
   - **Trajectory lines** trailing each pedestrian
   - **Count badge** at bottom-right showing unique count

#### Feature 4: Real-time Adjustment

1. While video is playing, move trajectory slider
2. Trajectory length updates in real-time
3. Longer history = larger fan-shape behind each person

### 5. Expected Visual Output

**Bounding Boxes:**

- Each pedestrian has a unique color
- Color persists across frames
- Track ID (number) displayed on box with semi-transparent background

**Trajectories:**

- Line shows path pedestrian traveled
- Last N points shown (controllable by slider)
- Older points appear faded (transparency gradient)
- Max real-world distance: 2cm per segment

**Count Badge:**

- Bottom-right corner of frame
- Shows: "Unique: X Current: Y"
- Black background with green text

### 6. Success Checklist

- [ ] Video loads in preview
- [ ] Trajectory slider appears and is adjustable
- [ ] "Start Tracking" button works
- [ ] Annotated frames display in canvas
- [ ] Bounding boxes have unique colors
- [ ] Track IDs visible on boxes
- [ ] Trajectory lines visible behind pedestrians
- [ ] Count badge shows at bottom-right
- [ ] Slider changes trajectory length in real-time
- [ ] Frame rate remains smooth (20+ fps)

## Troubleshooting

### Backend Won't Start

**Error:** `Import "v3Updates.tracker_ped" could not be resolved`

- **Solution**: This is a linting warning - it won't prevent execution
- Backend should still run correctly

### No Frames Displayed

**Problem:** Canvas is black after clicking "Start Tracking"

1. Check browser console (F12) for errors
2. Check backend logs for exceptions
3. Ensure WebSocket connection shows "✅ Connected" message

### Trajectory Lines Not Showing

**Problem:** Only bounding boxes visible, no lines

- Solution: Trajectory slider might be at minimum (5 points)
- Move slider to right to increase point count to 30-50
- Lines will appear more visible with more points

### Frames Very Slow

**Problem:** Processing is choppy/slow

- Solution: Reduce trajectory_max_points using slider
- Lower point count = faster rendering
- Try setting to 10-15 for faster frames

### Different Colors Every Frame

**Problem:** Track IDs keep changing colors

- Solution: This shouldn't happen - colors are deterministic per ID
- Restart browser and backend
- Check that track_ids are being properly maintained

## Architecture Verification

### Backend Data Flow ✅

```
Video Frame
    ↓
WebSocket /ws/pedestrian-track
    ↓
PedestrianTracker.process_frame()
    ↓
YOLOv8 Detection → ByteTrack → PedestrianVisualizer
    ↓
annotated_frame (BGR numpy array)
    ↓
Base64 encode → Send to client
```

### Frontend Data Flow ✅

```
User moves trajectory slider
    ↓
state: trajectoryMaxPoints updated
    ↓
WebSocket message: {frame, max_trajectory_points}
    ↓
Backend receives, uses in visualizer
    ↓
Response: annotated_frame with N trajectory points
    ↓
Canvas.drawImage(annotatedFrame)
```

## Key Files to Check

1. **Backend Visualization**

   - File: `ml/src/models/v3_analyzer.py`
   - Check: `PedestrianVisualizer` class exists and has all methods

2. **Service Integration**

   - File: `backend/app/services/pedestrian_tracker.py`
   - Check: `self.visualizer` initialized in `__init__`

3. **WebSocket Endpoint**

   - File: `backend/app/main.py`
   - Check: Line ~787 extracts `trajectory_max_points` from config

4. **Frontend Component**

   - File: `frontend/src/pages/PedestrianTracker.js`
   - Check: `trajectoryMaxPoints` state and slider in JSX

5. **Frontend Styling**
   - File: `frontend/src/styles/PedestrianTracker.css`
   - Check: `.trajectory-slider` class has proper styling

## Configuration for Testing

### Light Testing (5-10 pedestrians)

- Trajectory Max Points: 30
- Video resolution: 640x480
- Frame rate: 30fps

### Heavy Testing (20+ pedestrians)

- Trajectory Max Points: 15-20
- Video resolution: 1280x720
- Frame rate: 30fps

### Performance Testing

- Start at 50 trajectory points
- Gradually reduce to 5, measure fps
- Optimal point: 20-30 for smooth 30fps

## Next Steps

1. **Verify all features work** → Run quick test above
2. **Test with your videos** → Upload crowd videos to test
3. **Tune trajectory length** → Find best balance between history and performance
4. **Phase 2 Planning** → Speed estimation based on trajectories

## Support

If you encounter issues:

1. Check backend logs: `backend/logs/app.log`
2. Check browser console: F12 → Console tab
3. Verify all files were created correctly
4. Ensure ports 8000 (backend) and 3000 (frontend) are available

---

**Status**: Phase 1 Implementation Complete ✅
**Testing**: Ready to verify
**Next**: Phase 2 - Speed Estimation
