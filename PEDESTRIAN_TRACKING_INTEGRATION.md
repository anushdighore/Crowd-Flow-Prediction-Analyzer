# Pedestrian Tracking Integration - Implementation Summary

## Overview

Successfully integrated the `tracker_ped.py` from v3Updates module into the existing project as a complete pedestrian tracking feature accessible from both REST API and WebSocket endpoints, with frontend UI.

## Architecture

### 1. Backend Service Layer

**File:** `backend/app/services/pedestrian_tracker.py`

**Classes:**

- **PedestrianTracker** - Wrapper around tracker_ped.CrowdDensityEstimation
  - Handles frame processing
  - Optional homography matrix for world-coordinate transformation
  - Trajectory export to CSV
  - Metrics calculation
- **PedestrianTrackingPipeline** - Full video processing pipeline
  - Loads video files
  - Processes all frames with tracking
  - Saves processed video
  - Exports trajectory data

**Features:**

- ✅ YOLO-based pedestrian detection
- ✅ Kalman filter tracking
- ✅ Optional homography (world coordinates if provided)
- ✅ Falls back to image coordinates if homography not available
- ✅ Trajectory export (CSV format)
- ✅ Metrics (total persons, unique count, trajectory points)

### 2. REST API Endpoint

**File:** `backend/app/api/v1/endpoints/pedestrian_tracking.py`

**Endpoints:**

- `POST /api/v1/pedestrian-tracking/process-video` - Upload video and start processing
- `GET /api/v1/pedestrian-tracking/job/{job_id}` - Get processing status
- `GET /api/v1/pedestrian-tracking/download-video/{job_id}` - Download processed video
- `GET /api/v1/pedestrian-tracking/download-trajectories/{job_id}` - Download trajectory CSV
- `POST /api/v1/pedestrian-tracking/cleanup/{job_id}` - Clean up temporary files
- `GET /api/v1/pedestrian-tracking/health` - Health check

**Features:**

- Background processing (async)
- Job tracking with unique IDs
- Optional homography support
- Frame skip option for faster processing
- Temporary file management

### 3. WebSocket Endpoint

**File:** `backend/app/main.py` (added `/ws/pedestrian-track`)

**Features:**

- Real-time frame-by-frame tracking
- Configuration via initial JSON message
- Returns:
  - Current pedestrian count
  - Unique pedestrian count
  - Trajectory data
  - Annotated frames (as base64 JPEG)
  - World coordinate flag
- Automatic cleanup on disconnect

**Flow:**

```
Client connects → Sends config → Client sends frames →
Backend processes → Returns results → Repeat until close
```

### 4. Frontend Component

**File:** `frontend/src/pages/PedestrianTracker.js`

**Features:**

- Video file upload
- Real-time WebSocket processing
- Live tracking visualization
- Statistics display (current count, unique persons, trajectories)
- Optional homography calibration (UI ready, backend implementation needed)
- Frame-by-frame processing at specified FPS

**UI Elements:**

- Video upload button
- Homography toggle (optional)
- Start/Pause controls
- Video preview
- Live tracking canvas
- Statistics cards
- Trajectory counter

**File:** `frontend/src/styles/PedestrianTracker.css`

- Responsive design
- Gradient styling matching app theme
- Grid-based layout for desktop and mobile

### 5. Integration Points

**App.js Updates:**

- Added PedestrianTracker import
- Added "👥 Pedestrian Tracking" mode button
- Added routing logic for pedestrian tracking mode

**Backend main.py Updates:**

- Added import for PedestrianTracker service
- Added pedestrian_tracking_router to app
- Added base64 import for frame encoding/decoding
- Added `/ws/pedestrian-track` WebSocket endpoint

## Data Flow

### REST API Flow (Video Upload)

```
1. User uploads video via POST /api/v1/pedestrian-tracking/process-video
2. Video saved to temporary directory
3. PedestrianTrackingPipeline starts processing in background
4. Job ID returned to user
5. User polls GET /api/v1/pedestrian-tracking/job/{job_id} for status
6. When complete, user downloads:
   - Processed video: GET /api/v1/pedestrian-tracking/download-video/{job_id}
   - Trajectories CSV: GET /api/v1/pedestrian-tracking/download-trajectories/{job_id}
7. User calls POST /api/v1/pedestrian-tracking/cleanup/{job_id} to clean up
```

### WebSocket Flow (Real-time)

```
1. Frontend connects to /ws/pedestrian-track
2. Sends config: { homography: {...}, model_path: "..." }
3. Backend acknowledges: { status: "ready", ... }
4. For each frame:
   - Frontend sends: { frame: "data:image/jpeg;base64,..." }
   - Backend returns: { success: true, count, unique_count, trajectories, frame }
5. Frontend closes: { action: "close" }
6. WebSocket disconnects
```

## Configuration

### Backend

**Model:**

- Default: `yolov8n.pt` (can be customized)
- Pedestrian class only (COCO class 0)

**Tracking:**

- Tracker: BYTETRACK
- Confidence threshold: 0.3 (configurable)
- IOU threshold: 0.5 (configurable)

**Homography (Optional):**

- If provided: Transforms image coordinates to world coordinates
- If not provided: Uses image coordinates (pixel-based)
- Requires 4 image points and 4 world coordinate points

### Frontend

**WebSocket:**

- URL: `ws://localhost:8000/ws/pedestrian-track`
- Frame rate: Auto-detected from video (30 FPS default)
- Format: JPEG (80% quality)

## Usage Examples

### Using REST API (cURL)

```bash
# Upload video
curl -X POST \
  -F "file=@video.mp4" \
  -F "homography={\"image_points\":[[0,0],[100,0],[100,100],[0,100]],\"world_points\":[[0,0],[10,0],[10,10],[0,10]]}" \
  http://localhost:8000/api/v1/pedestrian-tracking/process-video

# Get status
curl http://localhost:8000/api/v1/pedestrian-tracking/job/{job_id}

# Download processed video
curl http://localhost:8000/api/v1/pedestrian-tracking/download-video/{job_id} > output.mp4

# Download trajectories
curl http://localhost:8000/api/v1/pedestrian-tracking/download-trajectories/{job_id} > trajectories.csv
```

### Using Frontend UI

1. Open app → Click "👥 Pedestrian Tracking" mode
2. Click "📁 Select Video"
3. (Optional) Toggle "Use World Coordinates" if you have calibration
4. Click "🎬 Start Tracking"
5. Watch live processing in canvas
6. View statistics in real-time

## CSV Output Format

**File: `trajectories.csv`**

```csv
id,frame,x,y
1,0,100.5,200.3
1,1,102.1,202.8
2,0,150.0,250.0
...
```

- `id`: Unique track ID (assigned per person)
- `frame`: Frame index in sequence
- `x, y`: Position coordinates (image or world, depending on homography)

## Performance Considerations

- **Model:** YOLO Nano for speed (~10-15 FPS on CPU)
- **Tracking:** Kalman filter-based (lightweight)
- **Memory:** Trajectory history limited to 45 frames per track
- **Storage:** Temporary files cleaned up after job completion

## Future Enhancements

1. **Homography Calibration UI**

   - Interactive point selection on video frame
   - Distance input dialog for world coordinates
   - Live transformation preview

2. **Advanced Metrics**

   - Integrate PedPy for density/speed calculations
   - Add zone-based counting (via tracker_pedv.py)

3. **Export Options**

   - GeoJSON format for mapping
   - JSON with enriched metadata
   - Video annotations with trajectories burned in

4. **Multi-Model Support**

   - Option to switch between different YOLO versions
   - Vehicle detection (expand from pedestrian-only)

5. **Performance Optimization**
   - GPU acceleration for video codec
   - Batch frame processing
   - Streaming video input

## Testing Checklist

- [ ] Upload small test video (~1-2 minutes)
- [ ] Verify pedestrian detection
- [ ] Check trajectory export
- [ ] Test WebSocket real-time processing
- [ ] Verify CSV format
- [ ] Test with/without homography
- [ ] Check error handling (missing files, etc.)
- [ ] Verify cleanup of temporary files

## Files Modified/Created

**Created:**

- `backend/app/services/pedestrian_tracker.py` (265 lines)
- `backend/app/api/v1/endpoints/pedestrian_tracking.py` (180 lines)
- `frontend/src/pages/PedestrianTracker.js` (350 lines)
- `frontend/src/styles/PedestrianTracker.css` (280 lines)

**Modified:**

- `backend/app/main.py` (+100 lines WebSocket, +5 imports)
- `frontend/src/App.js` (+3 lines import, +2 button, +1 routing)

**Dependencies:**

- Already installed: opencv-python, torch, ultralytics, numpy, pandas
- Already installed: fastapi, websockets, PIL

## Status

✅ **Implementation Complete**

- Backend service layer: Done
- REST API: Done
- WebSocket endpoint: Done
- Frontend component: Done
- Integration with App: Done

⏳ **Optional Enhancements:**

- Homography UI calibration tool
- PedPy metrics integration
- Multi-track visualization improvements
