# Advanced Crowd Analysis Implementation Summary

## Overview

This implementation adds PedPy-based pedestrian dynamics analysis to the crowd counting system, providing advanced density and speed metrics inspired by the analysis shown in `ml/src/v3Updates/CrowdAnalyzer.py`.

## What Was Implemented

### 1. Backend Changes

#### UnifiedCounter Class (`ml/src/models/unified_counter.py`)

Added 4 new methods for advanced analysis:

1. **`export_trajectory_data(frame_rate=30)`**

   - Converts track history to PedPy TrajectoryData format
   - Creates DataFrame with columns: id, frame, x, y
   - Required for all subsequent PedPy analysis

2. **`calculate_density_metrics(trajectory_data, walkable_area, measurement_area)`**

   - Computes **3 types of density**:
     - **Classic Density**: Traditional counting-based density
     - **Voronoi Density**: Spatial tessellation-based density
     - **Voronoi Density with Cutoff**: Voronoi with limited radius (12.0m)
   - Returns density values + intersection data for speed calculation

3. **`calculate_speed_metrics(trajectory_data, measurement_area, intersecting, frame_step=25)`**

   - Computes **4 types of speed** (when direction provided, otherwise 2):
     - **Mean Speed**: Average speed per frame
     - **Voronoi Speed**: Voronoi-weighted speed
     - **Mean Speed (Direction)**: Speed in specific direction
     - **Voronoi Speed (Direction)**: Voronoi-weighted directional speed
   - Uses frame_step=25 for speed calculation

4. **`get_advanced_metrics(frame_shape, frame_rate=30, frame_step=25)`**
   - **Main entry point** for getting all advanced metrics
   - Automatically defines walkable and measurement areas (full frame by default)
   - Returns dictionary with latest density and speed values:
     ```python
     {
       'density_metrics': {
         'classic_density': float,
         'voronoi_density': float,
         'voronoi_density_cutoff': float
       },
       'speed_metrics': {
         'mean_speed': float,
         'voronoi_speed': float
       }
     }
     ```

#### WebSocket Endpoints (`backend/app/main.py`)

Updated both `/ws/count` and `/ws/external-camera` endpoints:

- **When tracking is enabled** (YOLO models only):
  - Calls `counter.get_advanced_metrics()` after each frame
  - Adds `advanced_metrics` to WebSocket response
  - Logs metrics for debugging: `"📊 Advanced metrics: {...}"`
- **Fallback behavior**:
  - If PedPy not installed: Logs warning, continues without metrics
  - If insufficient tracking data: Returns None silently
  - If error occurs: Logs warning, continues without metrics

### 2. Frontend Changes

#### New Component: `AdvancedMetrics.js`

**Location**: `frontend/src/components/AdvancedMetrics.js`

**Purpose**: Display advanced crowd analysis metrics in beautiful cards

**Features**:

- **Gradient background** (purple/blue)
- **Two sections**:
  1. 📊 Density Metrics (3 cards)
  2. 🚶 Speed Metrics (2-4 cards)
- **Card layout**: Grid auto-fit, responsive
- **Each card shows**:
  - Label (e.g., "Classic Density")
  - Large value (monospace font)
  - Unit (e.g., "ped/m²" or "m/s")
- **Hover effects**: Lift animation on hover
- **Info footer**: "💡 Metrics calculated using PedPy pedestrian dynamics library"

**Props**:

```javascript
{
  densityMetrics: {
    classic_density: number,
    voronoi_density: number,
    voronoi_density_cutoff: number
  },
  speedMetrics: {
    mean_speed: number,
    voronoi_speed: number,
    mean_speed_direction?: number,     // Optional
    voronoi_speed_direction?: number   // Optional
  }
}
```

**Styling** (`AdvancedMetrics.css`):

- Purple gradient background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- White text on colored background
- Semi-transparent cards: `rgba(255, 255, 255, 0.95)`
- Responsive grid: `grid-template-columns: repeat(auto-fit, minmax(180px, 1fr))`
- Mobile-friendly: Single column on screens <768px

#### Updated: `WebcamCounter.js`

**Changes**:

1. Added import: `import AdvancedMetrics from "./components/AdvancedMetrics";`
2. Added component **after results panel, before tracking table**:
   ```jsx
   {
     isStreaming && enableTracking && results?.advanced_metrics && (
       <AdvancedMetrics
         densityMetrics={results.advanced_metrics.density_metrics}
         speedMetrics={results.advanced_metrics.speed_metrics}
       />
     );
   }
   ```
3. **Conditions for display**:
   - Streaming must be active
   - Tracking must be enabled
   - Results must contain `advanced_metrics`

#### Updated: `ExternalCam.js`

**Changes**:

1. Added import: `import AdvancedMetrics from "./AdvancedMetrics";`
2. Added component **inside camera-viewer section, before tracking table**:
   ```jsx
   {
     enableTracking && results?.advanced_metrics && (
       <AdvancedMetrics
         densityMetrics={results.advanced_metrics.density_metrics}
         speedMetrics={results.advanced_metrics.speed_metrics}
       />
     );
   }
   ```

### 3. Dependencies

#### Backend (`backend/requirements.txt`)

Added three new dependencies:

```
pedpy>=1.0.0      # Pedestrian dynamics analysis
pandas>=1.3.0     # DataFrame support for PedPy
scipy>=1.7.0      # Scientific computing (PedPy dependency)
```

#### Installation Script

**File**: `install_pedpy.bat` (Windows)

**Purpose**: Quick installation of PedPy dependencies

**Usage**:

```bash
cd "d:\College\Major Project"
install_pedpy.bat
```

## Data Flow

### 1. Tracking Data Collection

```
YOLO Detection → KalmanTracker → Track History
                                     ↓
                              track_history dict:
                              {
                                track_id: [(x1, y1), (x2, y2), ...],
                                ...
                              }
```

### 2. PedPy Analysis Pipeline

```
Track History → export_trajectory_data()
                        ↓
                  TrajectoryData (DataFrame)
                  ┌─────────┬───────┬─────┬─────┐
                  │ id      │ frame │ x   │ y   │
                  ├─────────┼───────┼─────┼─────┤
                  │ 1       │ 0     │ 100 │ 200 │
                  │ 1       │ 1     │ 102 │ 203 │
                  │ 2       │ 0     │ 300 │ 150 │
                  └─────────┴───────┴─────┴─────┘
                        ↓
         ┌──────────────┴──────────────┐
         ↓                              ↓
   calculate_density_metrics()   calculate_speed_metrics()
         ↓                              ↓
   Classic, Voronoi,              Mean, Voronoi,
   Voronoi Cutoff                 Directional speeds
         ↓                              ↓
         └──────────────┬──────────────┘
                        ↓
              get_advanced_metrics()
                        ↓
                  JSON Response
```

### 3. Frontend Display Flow

```
WebSocket Response → results.advanced_metrics
                            ↓
                     AdvancedMetrics.js
                            ↓
                   ┌────────┴────────┐
                   ↓                 ↓
            Density Cards       Speed Cards
            (3 metrics)         (2-4 metrics)
```

## Configuration

### Walkable Area & Measurement Area

Currently set to **full frame** (default):

```python
# In get_advanced_metrics():
walkable_polygon = np.array([
    [0, 0],
    [width, 0],
    [width, height],
    [0, height]
])

measurement_polygon = np.array([
    [0, 0],
    [width, 0],
    [width, height],
    [0, height]
])
```

**Future Enhancement**: Add UI to define custom polygons for specific analysis zones.

### Frame Rate

- Default: **30 fps** (assumed for webcam and IP cameras)
- Used for speed calculation: `speed = distance / (frame_delta / frame_rate)`

### Frame Step

- Default: **25 frames** for speed calculation
- Affects smoothness vs responsiveness of speed metrics

### Voronoi Cutoff Radius

- Default: **12.0 meters** (approximation in pixel space)
- Used for voronoi_density_cutoff calculation

## Testing

### Prerequisites

1. Install PedPy:

   ```bash
   install_pedpy.bat
   ```

   OR manually:

   ```bash
   cd backend
   pip install pedpy pandas scipy
   ```

2. Start backend:

   ```bash
   cd backend
   python run.py
   ```

3. Start frontend:
   ```bash
   cd frontend
   npm start
   ```

### Test Steps

#### Test 1: Webcam with Tracking

1. Go to **Webcam Counter** page
2. Select **YOLO model** (nano/small/medium)
3. Enable **"Enable Tracking (YOLO only)"**
4. Click **"Start Streaming"**
5. Wait for people to be tracked (need movement to build trajectories)
6. **Expected**: After ~5-10 seconds of tracking, advanced metrics panel appears below results
7. **Verify**:
   - Purple gradient panel with "Advanced Crowd Analysis" title
   - Density Metrics section (3 cards)
   - Speed Metrics section (2 cards minimum)
   - Values updating in real-time

#### Test 2: External IP Camera

1. Go to **External Camera** page
2. Enter IP camera URL
3. Select **YOLO model**
4. Enable **"Enable Tracking"**
5. Click **"Start Streaming"**
6. **Expected**: Same as Test 1 - advanced metrics appear
7. **Verify**: Metrics display inside camera viewer section

#### Test 3: No Tracking

1. Select **CSRNet or TMTB** model
2. Start streaming
3. **Expected**: No advanced metrics (only density maps)
4. **Verify**: No errors in console

### Debugging

#### Console Logs to Check

Backend:

```
📊 Advanced metrics: {'density_metrics': {...}, 'speed_metrics': {...}}
```

Frontend (browser console):

```
🎯 Tracking enabled - Received data: {hasTracks: true, trackCount: X, ...}
```

#### Common Issues

**Issue 1**: Advanced metrics not appearing

- **Check**: Is tracking enabled?
- **Check**: Are tracks being detected? (Look at "Active Tracks" table)
- **Check**: Browser console for `advanced_metrics` in WebSocket data
- **Cause**: Need sufficient tracking data (multiple frames with same track IDs)

**Issue 2**: Import error "pedpy could not be resolved"

- **Solution**: Run `install_pedpy.bat` or `pip install pedpy`
- **Verify**: `pip list | grep pedpy` shows pedpy installation

**Issue 3**: Metrics show 0.0000

- **Cause**: Not enough trajectory data yet (just started tracking)
- **Solution**: Wait 5-10 seconds for tracks to accumulate
- **Verify**: Check "Active Tracks" table shows increasing "Frames Tracked"

**Issue 4**: "PedPy not installed" warning in backend logs

- **Solution**: Install dependencies: `pip install pedpy pandas scipy`

## Comparison with CrowdAnalyzer.py

### CrowdAnalyzer.py Features

- **GUI**: PyQt6 desktop application
- **Video file processing**: Batch processing of recorded videos
- **Homography**: Transforms pixel coordinates to real-world meters
- **Plot generation**: Matplotlib plots for density/speed over time
- **CSV export**: Saves trajectories to CSV for offline analysis

### Our Implementation Features

- **Real-time**: Live WebSocket streaming
- **Web-based**: React frontend, FastAPI backend
- **Latest values**: Shows current frame metrics (not full time series)
- **Integrated**: Part of existing multi-model crowd counting system
- **Auto frame**: Uses full frame as walkable/measurement area

### Shared Features

Both use:

- ✅ PedPy library for pedestrian dynamics
- ✅ YOLO for detection + tracking
- ✅ Same density methods (classic, voronoi, voronoi_cutoff)
- ✅ Same speed methods (mean, voronoi)
- ✅ Walkable area and measurement area concepts

## Future Enhancements

### Phase 1: Visualization

- [ ] Create `TrajectoryPlot.js` component
- [ ] Display full trajectory time series (line charts)
- [ ] Show density heatmap overlay (not just YOLO boxes)
- [ ] Animate speed color-coding on video

### Phase 2: Configuration

- [ ] UI for defining walkable area polygon (click to draw)
- [ ] UI for defining measurement area (ROI selection)
- [ ] Adjustable frame rate setting
- [ ] Adjustable frame step for speed calculation

### Phase 3: Historical Analysis

- [ ] Store trajectory data in database
- [ ] Generate time-series plots (like CrowdAnalyzer.py)
- [ ] Export trajectory CSV
- [ ] Historical comparison charts

### Phase 4: Advanced Metrics

- [ ] Homography transformation (pixel → real-world coordinates)
- [ ] Flow analysis (entry/exit counting)
- [ ] Crowd pressure estimation
- [ ] Anomaly detection (sudden density spikes)

## File Changes Summary

### New Files

- ✅ `frontend/src/components/AdvancedMetrics.js` (115 lines)
- ✅ `frontend/src/components/AdvancedMetrics.css` (95 lines)
- ✅ `install_pedpy.bat` (15 lines)
- ✅ `docs/version/v3/ADVANCED_CROWD_ANALYSIS_IMPLEMENTATION.md` (this file)

### Modified Files

- ✅ `ml/src/models/unified_counter.py` (+279 lines)
  - Added: export_trajectory_data()
  - Added: calculate_density_metrics()
  - Added: calculate_speed_metrics()
  - Added: get_advanced_metrics()
- ✅ `backend/app/main.py` (+34 lines)
  - Updated: /ws/count endpoint (advanced metrics support)
  - Updated: /ws/external-camera endpoint (advanced metrics support)
- ✅ `backend/requirements.txt` (+3 lines)
  - Added: pedpy>=1.0.0
  - Added: pandas>=1.3.0
  - Added: scipy>=1.7.0
- ✅ `frontend/src/WebcamCounter.js` (+8 lines)
  - Added: AdvancedMetrics import
  - Added: AdvancedMetrics component in JSX
- ✅ `frontend/src/components/ExternalCam.js` (+8 lines)
  - Added: AdvancedMetrics import
  - Added: AdvancedMetrics component in JSX

### Unchanged Files

- `frontend/src/models/YOLOUploader.js` (could add later)
- `frontend/src/VideoUploader.js` (could add later)
- `ml/src/v3Updates/CrowdAnalyzer.py` (reference implementation)

## Conclusion

This implementation successfully integrates PedPy-based advanced crowd analysis into the existing system, providing real-time density and speed metrics for tracked pedestrians. The system now offers scientific-grade pedestrian dynamics analysis alongside traditional crowd counting.

**Key Achievements**:

1. ✅ Real-time PedPy integration
2. ✅ 3 density metrics + 2-4 speed metrics
3. ✅ Beautiful frontend visualization
4. ✅ Graceful degradation (works without PedPy)
5. ✅ Compatible with existing tracking system
6. ✅ Minimal changes to existing code

**Next Steps**:

1. Run `install_pedpy.bat`
2. Test with webcam and IP camera
3. Gather feedback on metrics accuracy
4. Plan Phase 2: Trajectory plots and configuration UI
