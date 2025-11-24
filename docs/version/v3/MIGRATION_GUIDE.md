# Migration Guide: Integrating V3 Features

## Overview

This guide provides step-by-step instructions for integrating V3 features (tracking, PedPy, homography) into the existing Crowd Flow Prediction Analyzer system **without breaking current functionality**.

## Integration Strategy

### Phase 1: ML Testing & Validation ✅ (Current)

1. Set up test infrastructure
2. Test existing models (CSRNet, YOLO)
3. Test V3 tracking algorithms
4. Validate integration points

### Phase 2: Core ML Integration (Next)

1. Move V3 modules to production
2. Create unified model interfaces
3. Add configuration options

### Phase 3: API Updates

1. Extend existing endpoints
2. Add new V3-specific endpoints
3. Maintain backward compatibility

### Phase 4: Frontend Integration

1. Update UI for new features
2. Add visualization components
3. Progressive enhancement

---

## Phase 1: ML Testing (CURRENT)

### Step 1.1: Verify Test Structure

```bash
# Check test directories exist
cd ml
ls tests/csrnet tests/yolo tests/mcnn tests/tracking tests/integration

# Run tests
pytest tests/ -v
```

### Step 1.2: Add Test Data

```bash
# Add sample images to data/
cp your_crowd_images/* data/images/crowd/medium_density/
cp your_videos/* data/videos/test_samples/
```

### Step 1.3: Run Model Tests

```bash
# Test CSRNet
pytest tests/csrnet/ -v -s

# Test YOLO detection
pytest tests/yolo/test_detection.py -v -s

# Test V3 tracking
pytest tests/yolo/test_tracking.py -v -s
```

**Expected Output:**

- ✅ All models load successfully
- ✅ Predictions are reasonable
- ✅ Performance meets benchmarks

---

## Phase 2: Core ML Integration

### Step 2.1: Organize V3 Modules

**Create production tracking module:**

```bash
cd ml/src
mkdir -p models/tracking
```

**File: `ml/src/models/tracking/__init__.py`**

```python
"""
V3 Tracking Module
Unified interface for tracking algorithms
"""
from .kalman_tracker import KalmanTracker
from .multi_object_tracker import MultiObjectTracker

__all__ = ['KalmanTracker', 'MultiObjectTracker']
```

**File: `ml/src/models/tracking/kalman_tracker.py`**

```python
"""
Kalman Filter Tracking
Extracted from v3Updates/tracker_ped.py
"""
import numpy as np
from filterpy.kalman import KalmanFilter
from scipy.optimize import linear_sum_assignment

class Track:
    """Individual track with Kalman filter"""
    # Copy Track class from v3Updates/tracker_ped.py
    pass

class KalmanTracker:
    """Main tracking interface"""
    def __init__(self, conf_threshold=0.3, iou_threshold=0.45):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.tracks = []
        self.next_id = 0

    def update(self, detections):
        """Update tracks with new detections"""
        # Implement from v3Updates
        pass

    def get_tracks(self):
        """Get active tracks"""
        return [t for t in self.tracks if t.state == TrackState.TRACKED]
```

### Step 2.2: Create Unified Model Interface

**File: `ml/src/models/unified_counter.py`**

```python
"""
Unified Crowd Counter
Supports multiple models + optional tracking
"""
from typing import Dict, Optional, List
import numpy as np

class UnifiedCounter:
    """Unified interface for all counting models"""

    def __init__(
        self,
        model_type: str = 'yolo',  # 'yolo', 'csrnet', 'mcnn'
        enable_tracking: bool = False,
        **kwargs
    ):
        self.model_type = model_type
        self.enable_tracking = enable_tracking

        # Load appropriate model
        if model_type == 'yolo':
            from models.yolo.yolov8_counter import YOLOv8Counter
            self.model = YOLOv8Counter(**kwargs)
        elif model_type == 'csrnet':
            from models.csrnet.model import CSRNet
            self.model = CSRNet(**kwargs)
        elif model_type == 'mcnn':
            from models.mcnn.model import MCNN
            self.model = MCNN(**kwargs)

        # Optional tracking
        self.tracker = None
        if enable_tracking and model_type == 'yolo':
            from models.tracking import KalmanTracker
            self.tracker = KalmanTracker()

    def predict(self, image, return_details=False):
        """Unified prediction interface"""
        result = self.model.predict(image)

        # Add tracking if enabled
        if self.tracker and 'boxes' in result:
            self.tracker.update(result['boxes'])
            tracks = self.tracker.get_tracks()
            result['tracks'] = tracks
            result['unique_count'] = len(set(t.id for t in tracks))

        return result
```

### Step 2.3: Update Configuration

**File: `backend/config.yaml` (Add V3 section)**

```yaml
models:
  # Existing configs
  csrnet:
    checkpoint: "ml/checkpoints/csrnet.pth"
    device: "cuda"

  yolo:
    model: "yolov8n.pt"
    conf_threshold: 0.25
    iou_threshold: 0.45

  # NEW: V3 features
  tracking:
    enabled: false # Set to true to enable
    tracker_type: "kalman" # or "bytetrack"
    max_age: 10
    min_hits: 3

  homography:
    enabled: false
    calibration_file: "data/calibration/homography_points.json"

  pedpy:
    enabled: false
    frame_rate: 30
    walkable_area: null # Set via API
    measurement_area: null
```

### Step 2.4: Add Feature Flags

**File: `backend/app/core/config.py`**

```python
class Settings:
    # Existing settings...

    # V3 Feature Flags
    ENABLE_TRACKING: bool = False
    ENABLE_HOMOGRAPHY: bool = False
    ENABLE_PEDPY: bool = False

    class Config:
        env_file = ".env"
```

---

## Phase 3: API Updates

### Step 3.1: Extend Prediction Endpoint

**File: `backend/app/api/predict.py`**

```python
from pydantic import BaseModel
from typing import Optional, List, Dict

class PredictionRequest(BaseModel):
    # Existing fields
    model: str = "yolo"

    # NEW: V3 options
    enable_tracking: bool = False
    enable_homography: bool = False
    homography_points: Optional[List[List[float]]] = None

class PredictionResponse(BaseModel):
    # Existing fields
    count: int

    # NEW: V3 fields (optional)
    tracks: Optional[List[Dict]] = None
    unique_count: Optional[int] = None
    trajectories: Optional[List[Dict]] = None
    world_coordinates: bool = False

@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Enhanced prediction with optional V3 features"""

    # Use unified counter
    counter = UnifiedCounter(
        model_type=request.model,
        enable_tracking=request.enable_tracking
    )

    result = counter.predict(image)

    return PredictionResponse(
        count=result['count'],
        tracks=result.get('tracks'),
        unique_count=result.get('unique_count')
    )
```

### Step 3.2: Add New V3 Endpoints

**File: `backend/app/api/tracking.py` (NEW)**

```python
from fastapi import APIRouter, UploadFile
from typing import List

router = APIRouter(prefix="/tracking", tags=["tracking"])

@router.post("/video")
async def track_video(
    file: UploadFile,
    model: str = "yolo11n",
    tracker: str = "bytetrack"
):
    """Process video with tracking"""
    # Implementation
    pass

@router.get("/trajectories/{video_id}")
async def get_trajectories(video_id: str):
    """Get trajectory data"""
    # Return CSV/JSON trajectories
    pass

@router.post("/calibrate")
async def set_homography(
    points_image: List[List[float]],
    points_world: List[List[float]]
):
    """Set homography calibration"""
    # Store calibration
    pass
```

### Step 3.3: Maintain Backward Compatibility

**Test existing endpoints still work:**

```python
# Old API calls should work unchanged
POST /api/predict
{
    "model": "yolo"  # No tracking fields
}

# Should return same response format
{
    "count": 25,
    "timestamp": "2025-11-10T..."
}
```

---

## Phase 4: Frontend Integration

### Step 4.1: Add Feature Toggle UI

**File: `frontend/src/components/SettingsPanel.js` (NEW)**

```javascript
import React, { useState } from "react";

export function SettingsPanel() {
  const [enableTracking, setEnableTracking] = useState(false);
  const [enableHomography, setEnableHomography] = useState(false);

  return (
    <div className="settings-panel">
      <h3>V3 Features (Beta)</h3>

      <label>
        <input
          type="checkbox"
          checked={enableTracking}
          onChange={(e) => setEnableTracking(e.target.checked)}
        />
        Enable Tracking (Persistent IDs)
      </label>

      <label>
        <input
          type="checkbox"
          checked={enableHomography}
          onChange={(e) => setEnableHomography(e.target.checked)}
        />
        Enable World Coordinates
      </label>
    </div>
  );
}
```

### Step 4.2: Update WebcamCounter Component

**File: `frontend/src/WebcamCounter.js`**

```javascript
// Add to state
const [enableTracking, setEnableTracking] = useState(false);
const [uniqueCount, setUniqueCount] = useState(0);

// Update API call
const sendFrame = async (frame) => {
  const response = await fetch("/api/predict", {
    method: "POST",
    body: JSON.stringify({
      model: selectedModel,
      enable_tracking: enableTracking, // NEW
    }),
  });

  const result = await response.json();
  setCount(result.count);

  // NEW: Handle tracking results
  if (result.unique_count) {
    setUniqueCount(result.unique_count);
  }
};

// Update display
return (
  <div>
    <p>Current Count: {count}</p>
    {enableTracking && <p>Unique Count: {uniqueCount}</p>}
  </div>
);
```

### Step 4.3: Add Trajectory Visualization

**File: `frontend/src/components/TrajectoryView.js` (NEW)**

```javascript
import React, { useEffect, useRef } from "react";

export function TrajectoryView({ trajectories }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!trajectories || trajectories.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // Draw trajectories
    trajectories.forEach((traj) => {
      ctx.strokeStyle = `hsl(${traj.id * 137.5}, 70%, 50%)`;
      ctx.beginPath();
      traj.points.forEach((p, i) => {
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      });
      ctx.stroke();
    });
  }, [trajectories]);

  return <canvas ref={canvasRef} width={800} height={600} />;
}
```

---

## Testing Integration

### Integration Test Checklist

```bash
# 1. Test ML models work
cd ml
pytest tests/ -v

# 2. Test backend still works
cd backend
python run.py
curl http://localhost:8000/api/predict  # Should work

# 3. Test frontend still works
cd frontend
npm start
# Open browser, test webcam counter

# 4. Test new features don't break old
# Make prediction with tracking=false
# Should get same result as before

# 5. Test new features work
# Make prediction with tracking=true
# Should get additional track data
```

### Rollback Plan

If integration breaks something:

1. **Disable feature flags** in `config.yaml`:

   ```yaml
   tracking:
     enabled: false
   ```

2. **Revert API changes** using git:

   ```bash
   git checkout main -- backend/app/api/predict.py
   ```

3. **Remove new endpoints** temporarily

4. **Keep old code path** always working

---

## Deployment

### Development Environment

```bash
# 1. Update dependencies
cd ml
pip install -r requirements.txt
pip install filterpy pedpy  # V3 dependencies

# 2. Run tests
pytest tests/ -v

# 3. Start backend with V3 disabled
cd backend
ENABLE_TRACKING=false python run.py
```

### Production Environment

```bash
# 1. Deploy with feature flags OFF
export ENABLE_TRACKING=false
export ENABLE_HOMOGRAPHY=false

# 2. Monitor metrics
# Check prediction latency, error rates

# 3. Gradually enable features
# Start with tracking on low-traffic endpoint
export ENABLE_TRACKING=true

# 4. Monitor and adjust
# If issues arise, disable immediately
```

---

## Next Steps

After successful integration:

1. ✅ Complete ML tests
2. ✅ Create unified model interface
3. ⏳ Update API endpoints
4. ⏳ Update frontend UI
5. ⏳ Add PedPy analytics dashboard
6. ⏳ Create desktop app (PyQt6)

**See:** [NEXT_ITERATIONS.md](./NEXT_ITERATIONS.md) for roadmap
