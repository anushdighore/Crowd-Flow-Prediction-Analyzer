# V3 Implementation Status & Next Phases

## Current Implementation Status

### ✅ CORE FEATURES COMPLETE (7/15 = 47%)

- ✅ YOLO Detection
- ✅ Kalman Tracking
- ✅ Hungarian Matching
- ✅ Trajectory Processing
- ✅ Unique Counting
- ✅ Unified Model Interface
- ✅ Frontend Tracking UI

### ⏳ PARTIALLY DONE (4/15 = 27%)

- ⏳ Density Analysis (50%)
- ⏳ Speed Analysis (0%)
- ⏳ Homography Transform (0%)
- ⏳ Trajectory Visualization (0%)
- ⏳ Zone Definition (0%)

### ❌ NOT STARTED (4/15 = 27%)

- ❌ Groq AI Integration
- ❌ Batch Processing
- ❌ Export Functionality

---

## PHASE 1: TRAJECTORY VISUALIZATION (2-3 days)

**Priority**: HIGH | **Impact**: Visual feedback critical for user acceptance

### 1.1 Draw Track Paths on Frame

**Files**: `frontend/src/WebcamCounter.js`

```javascript
// In canvas drawing:
if (enableTracking && results.tracks) {
  results.tracks.forEach((track) => {
    // Draw trajectory path
    context.strokeStyle = getTrackColor(track.id);
    context.lineWidth = 2;
    track.history.forEach((point, i) => {
      if (i === 0) context.moveTo(point.x, point.y);
      else context.lineTo(point.x, point.y);
    });
    context.stroke();

    // Draw track ID
    context.fillStyle = "white";
    context.font = "16px Arial";
    context.fillText(`#${track.id}`, track.position[0], track.position[1]);
  });
}
```

**Implementation Steps**:

1. Extract trajectory points from backend response
2. Draw lines connecting trajectory points
3. Color-code by track state (green=tracked, yellow=lost, red=new)
4. Display track ID on each object
5. Add trajectory fade-out over time

**Backend Changes Needed**: None (data already available)

---

### 1.2 Track History Display UI

**Files**: `frontend/src/WebcamCounter.js`, `frontend/src/App.css`

**Add to Results Panel**:

```jsx
{
  enableTracking && (
    <div className="tracking-details">
      <h3>Active Tracks</h3>
      <table>
        <thead>
          <tr>
            <th>Track ID</th>
            <th>Frames Tracked</th>
            <th>State</th>
            <th>Position</th>
          </tr>
        </thead>
        <tbody>
          {results.tracks?.map((t) => (
            <tr key={t.id}>
              <td>#{t.id}</td>
              <td>{t.frame_count || 0}</td>
              <td>{t.state}</td>
              <td>
                ({t.position[0]}, {t.position[1]})
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**CSS Additions**:

```css
.tracking-details {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.tracking-details table {
  width: 100%;
  border-collapse: collapse;
}

.tracking-details th,
.tracking-details td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
```

**Timeline**: 1 day

---

## PHASE 2: SPEED ANALYSIS (2-3 days)

**Priority**: HIGH | **Impact**: Critical for crowd flow analysis

### 2.1 Calculate Speed from Trajectories

**Files**: `ml/src/models/tracking/kalman_tracker.py`

```python
class Track:
    def __init__(self, detection, track_id, fps=30):
        # ... existing code ...
        self.fps = fps
        self.speeds = []  # Frame-by-frame speeds

    def calculate_speed(self, prev_position):
        """Calculate speed between current and previous position"""
        if prev_position is None:
            return 0

        # Euclidean distance
        distance = np.linalg.norm(
            np.array(self.position) - np.array(prev_position)
        )

        # Convert to pixels/second
        speed = distance * self.fps

        # Smooth with moving average
        self.speeds.append(speed)
        if len(self.speeds) > 10:
            self.speeds.pop(0)

        avg_speed = np.mean(self.speeds)
        return avg_speed
```

**Backend Changes**: Update `unified_counter.py`

```python
# In predict() method, after tracking update:
for track in self.tracker.tracks:
    speed = track.calculate_speed(track.prev_position)
    track_data['speed'] = speed
    track_data['avg_speed'] = np.mean(track.speeds)
```

**Timeline**: 1-2 days

---

### 2.2 Visualize Speed (Color Coding)

**Files**: `ml/src/models/unified_counter.py`

```python
def get_track_color(self, speed, max_speed=100):
    """Color code track by speed (blue=slow, red=fast)"""
    # Normalize speed 0-1
    norm_speed = min(speed / max_speed, 1.0)

    # Interpolate red-blue
    red = int(255 * norm_speed)
    blue = int(255 * (1 - norm_speed))

    return (blue, 0, red)  # BGR format

# In _draw_predictions():
for box, track_id, speed in zip(boxes, track_ids, speeds):
    color = self.get_track_color(speed)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
```

**Timeline**: 1 day

---

### 2.3 Speed Statistics Display

**Files**: `frontend/src/WebcamCounter.js`

```jsx
{
  enableTracking && results.speed_stats && (
    <div className="speed-stats">
      <h4>Speed Analytics</h4>
      <div className="stats-grid">
        <div className="stat-item">
          <span>Avg Speed:</span>
          <span>{results.speed_stats.average.toFixed(2)} px/s</span>
        </div>
        <div className="stat-item">
          <span>Max Speed:</span>
          <span>{results.speed_stats.max.toFixed(2)} px/s</span>
        </div>
        <div className="stat-item">
          <span>Min Speed:</span>
          <span>{results.speed_stats.min.toFixed(2)} px/s</span>
        </div>
      </div>
    </div>
  );
}
```

**Timeline**: 0.5 day

---

## PHASE 3: ADVANCED ANALYTICS (3-5 days)

**Priority**: MEDIUM | **Impact**: Valuable for research/insights

### 3.1 Voronoi Density Analysis

**Files**: `ml/src/models/tracking/kalman_tracker.py`

```python
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np

def calculate_voronoi_density(tracks, frame_height, frame_width):
    """Calculate personal space using Voronoi diagrams"""
    if len(tracks) < 3:
        return {}

    # Get all current positions
    positions = np.array([t.position for t in tracks])

    # Calculate Voronoi
    vor = Voronoi(positions)

    # Get personal space (area of each Voronoi cell)
    personal_space = {}
    for point_idx, region_idx in enumerate(vor.point_region):
        region = vor.regions[region_idx]
        if len(region) > 0:
            area = vor.area[region_idx]
            personal_space[tracks[point_idx].track_id] = area

    return personal_space
```

**Timeline**: 1-2 days

---

### 3.2 Crowd Flow Vectors

**Files**: `ml/src/models/tracking/kalman_tracker.py`

```python
def calculate_flow_vectors(tracks, frame_width, frame_height, grid_cells=5):
    """Divide frame into grid and calculate flow direction per cell"""
    cell_width = frame_width // grid_cells
    cell_height = frame_height // grid_cells

    flow_grid = {}

    for track in tracks:
        x, y = track.position
        cell_x, cell_y = int(x // cell_width), int(y // cell_height)
        cell_key = (cell_x, cell_y)

        if cell_key not in flow_grid:
            flow_grid[cell_key] = []

        # Add velocity vector
        vx, vy = track.kf.x[2], track.kf.x[3]  # Velocity from Kalman
        flow_grid[cell_key].append((vx, vy))

    # Calculate average flow per cell
    avg_flow = {}
    for cell, velocities in flow_grid.items():
        avg_vx = np.mean([v[0] for v in velocities])
        avg_vy = np.mean([v[1] for v in velocities])
        avg_flow[cell] = (avg_vx, avg_vy)

    return avg_flow
```

**Timeline**: 1 day

---

## PHASE 4: MULTI-CLASS TRACKING (2-3 days)

**Priority**: MEDIUM | **Impact**: Enables vehicle/pedestrian analysis

### 4.1 Implement Vehicle+Pedestrian Tracking

**Files**: Reference `ml/src/v3Updates/tracker_pedv.py`

```python
class MultiClassTracker:
    def __init__(self):
        self.pedestrian_tracker = KalmanTracker()
        self.vehicle_tracker = KalmanTracker()
        self.class_map = {
            'person': self.pedestrian_tracker,
            'car': self.vehicle_tracker,
            'bus': self.vehicle_tracker,
            'truck': self.vehicle_tracker,
            'bicycle': self.pedestrian_tracker,
            'motorcycle': self.vehicle_tracker
        }

    def update(self, detections, classes):
        """Update appropriate tracker based on class"""
        ped_dets = [d for d, c in zip(detections, classes) if c == 'person']
        vehicle_dets = [d for d, c in zip(detections, classes) if c != 'person']

        ped_tracks = self.pedestrian_tracker.update(ped_dets)
        vehicle_tracks = self.vehicle_tracker.update(vehicle_dets)

        return ped_tracks, vehicle_tracks
```

**Backend**: `backend/app/api/v1/endpoints/yolo.py`

```python
@router.post("/track/multi-class")
async def track_multi_class(file: UploadFile = File(...)):
    """Track pedestrians and vehicles separately"""
    ped_count = len(ped_tracks)
    vehicle_count = len(vehicle_tracks)
    unique_peds = max([t.id for t in ped_tracks], default=0)
    unique_vehicles = max([t.id for t in vehicle_tracks], default=0)

    return {
        "pedestrian_count": ped_count,
        "vehicle_count": vehicle_count,
        "unique_pedestrians": unique_peds,
        "unique_vehicles": unique_vehicles,
        "tracks": ped_tracks + vehicle_tracks
    }
```

**Timeline**: 2 days

---

### 4.2 Frontend Multi-Class Display

**Files**: `frontend/src/WebcamCounter.js`

```jsx
{
  enableTracking && results.pedestrian_count !== undefined && (
    <div className="multi-class-results">
      <div className="count-row">
        <span>👥 Pedestrians:</span>
        <span className="value">{results.pedestrian_count}</span>
        <span className="unique">Unique: {results.unique_pedestrians}</span>
      </div>
      <div className="count-row">
        <span>🚗 Vehicles:</span>
        <span className="value">{results.vehicle_count}</span>
        <span className="unique">Unique: {results.unique_vehicles}</span>
      </div>
    </div>
  );
}
```

**Timeline**: 0.5 day

---

## PHASE 5: EXPORT & REPORTING (2-3 days)

**Priority**: LOW | **Impact**: Data persistence for analysis

### 5.1 CSV Export Endpoint

**Files**: `backend/app/api/v1/endpoints/yolo.py`

```python
@router.get("/export/trajectories")
async def export_trajectories(session_id: str = Query(...)):
    """Export all trajectories from session as CSV"""
    # Get tracker from session manager
    tracker = session_manager.get_tracker(session_id)

    # Collect all trajectory data
    trajectory_data = []
    for track in tracker.tracks:
        for i, point in enumerate(track.history):
            trajectory_data.append({
                'track_id': track.id,
                'frame': track.frame_start + i,
                'x': point[0],
                'y': point[1],
                'state': str(track.state),
                'speed': track.speeds[i] if i < len(track.speeds) else 0
            })

    # Convert to CSV
    df = pd.DataFrame(trajectory_data)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    return {
        "csv": csv_buffer.getvalue(),
        "filename": f"trajectories_{session_id}.csv"
    }
```

**Timeline**: 1 day

---

### 5.2 Statistics Report

**Files**: `backend/app/api/v1/endpoints/yolo.py`

```python
@router.get("/stats/summary")
async def get_statistics(session_id: str = Query(...)):
    """Get session statistics summary"""
    tracker = session_manager.get_tracker(session_id)

    return {
        "total_frames": tracker.frame_count,
        "unique_objects": len(tracker.get_all_track_ids()),
        "avg_speed": np.mean([np.mean(t.speeds) for t in tracker.tracks]),
        "crowd_density_avg": np.mean(tracker.density_history),
        "processing_time_avg": np.mean(tracker.timing_history),
        "peak_count": max(tracker.frame_counts)
    }
```

**Timeline**: 1 day

---

## PHASE 6: GROQ AI INSIGHTS (2-3 days)

**Priority**: LOW | **Impact**: Marketing/presentation value

### 6.1 Integrate Groq API

**Files**: `backend/app/services/groq_analyzer.py`

```python
from groq import Groq

class GroqAnalyzer:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def analyze_statistics(self, stats):
        """Get AI insights from statistics"""
        prompt = f"""
        Analyze these crowd statistics and provide insights:
        - Total people: {stats['unique_objects']}
        - Average density: {stats['crowd_density_avg']}
        - Peak count: {stats['peak_count']}
        - Processing time: {stats['processing_time_avg']}

        Provide 2-3 key insights about crowd behavior.
        """

        message = self.client.messages.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text
```

**Backend Endpoint**: `backend/app/api/v1/endpoints/analytics.py`

```python
@router.post("/ai/insights")
async def get_ai_insights(stats: dict):
    """Get AI-generated insights from statistics"""
    analyzer = GroqAnalyzer(api_key=settings.GROQ_API_KEY)
    insights = analyzer.analyze_statistics(stats)
    return {"insights": insights}
```

**Timeline**: 1-2 days

---

## PHASE 7: BATCH PROCESSING (3-5 days)

**Priority**: LOW | **Impact**: Batch analysis capability

### 7.1 Video Batch Processing

**Files**: `backend/app/api/v1/endpoints/batch.py`

```python
@router.post("/batch/process")
async def process_batch(files: List[UploadFile], model: str = "yolo"):
    """Process multiple videos sequentially"""
    results = []

    for file in files:
        # Process each video
        video_path = f"/tmp/{file.filename}"
        with open(video_path, 'wb') as f:
            content = await file.read()
            f.write(content)

        # Run tracking
        result = process_video_with_tracking(video_path, model)
        results.append({
            "filename": file.filename,
            "stats": result
        })

        # Clean up
        os.remove(video_path)

    return {"results": results}
```

**Timeline**: 2-3 days

---

## Timeline Overview

```
Phase 1: Trajectory Visualization    |████ 2-3 days | HIGH PRIORITY
Phase 2: Speed Analysis              |████ 2-3 days | HIGH PRIORITY
Phase 3: Voronoi/Flow Analysis       |████ 3-5 days | MEDIUM
Phase 4: Multi-Class Tracking        |████ 2-3 days | MEDIUM
Phase 5: Export & Reporting          |███  2-3 days | LOW
Phase 6: Groq AI Insights            |███  2-3 days | LOW
Phase 7: Batch Processing            |███  3-5 days | LOW

Total Implementation Time: 16-25 days (with 1 developer)
```

---

## Recommended Execution Order

### Sprint 1 (Week 1-2): Core Visualization

1. **Phase 1**: Trajectory Visualization (2-3 days)
2. **Phase 2**: Speed Analysis (2-3 days)
3. **Testing**: End-to-end validation (2 days)

**Deliverable**: Full tracking UI with speed metrics

---

### Sprint 2 (Week 3): Analytics

1. **Phase 3**: Voronoi & Flow Analysis (3-5 days)
2. **Phase 4**: Multi-Class Tracking (2-3 days)

**Deliverable**: Advanced analytics with vehicle/pedestrian separation

---

### Sprint 3 (Week 4): Polish

1. **Phase 5**: Export & Reporting (2-3 days)
2. **Phase 6**: Groq AI (2-3 days)
3. **Phase 7**: Batch Processing (3-5 days - if time permits)

**Deliverable**: Production-ready system with data export

---

## Dependencies Installation

```bash
# Phase 2 (Speed) & Phase 3 (Voronoi)
pip install scipy>=1.7.0

# Phase 3 (PedPy integration - optional)
pip install pedpy>=0.5.0

# Phase 6 (Groq)
pip install groq>=0.4.0

# Phase 5 (Export)
pip install pandas>=1.3.0

# Phase 7 (Batch)
pip install celery>=5.1.0  # For async task queue
```

---

## Success Criteria by Phase

### Phase 1 ✅

- [ ] Trajectories drawn on video
- [ ] Track IDs visible
- [ ] Track history table populated
- [ ] Visual looks professional

### Phase 2 ✅

- [ ] Speed calculated per track
- [ ] Color-coded visualization (red=fast, blue=slow)
- [ ] Speed stats displayed
- [ ] Average speed accurate

### Phase 3 ✅

- [ ] Voronoi cells calculated
- [ ] Personal space metrics shown
- [ ] Flow vectors visualized
- [ ] Performance acceptable (< 50ms overhead)

### Phase 4 ✅

- [ ] Pedestrians tracked separately
- [ ] Vehicles tracked separately
- [ ] Unique counts correct for each class
- [ ] API returns multi-class data

### Phase 5 ✅

- [ ] CSV export working
- [ ] Statistics endpoint functional
- [ ] File format correct
- [ ] Data importable to Excel

### Phase 6 ✅

- [ ] Groq API integrated
- [ ] Insights generated automatically
- [ ] Insights relevant and accurate
- [ ] API key management secure

### Phase 7 ✅

- [ ] Multiple videos processed
- [ ] Results aggregated
- [ ] Progress tracking works
- [ ] Error handling robust

---

## Notes

- Each phase builds on the previous
- Can skip phases if not needed
- All code should maintain backward compatibility
- Tests required for each phase
- Documentation to be created in `docs/version/v3/` folder
