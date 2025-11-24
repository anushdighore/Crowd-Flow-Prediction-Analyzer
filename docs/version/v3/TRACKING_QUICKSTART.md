# V3 Tracking Implementation - Quick Start

## What Was Implemented

### ✅ Backend (Complete)

1. **KalmanTracker** (`ml/src/models/tracking/kalman_tracker.py`)

   - Kalman filter-based object tracking
   - Hungarian algorithm for detection-track matching
   - Track state management (NEW/TRACKED/LOST)
   - Trajectory history storage

2. **UnifiedCounter** (`ml/src/models/unified_counter.py`)

   - Unified interface for all models (YOLO, CSRNet, MCNN)
   - Optional tracking support
   - Feature flags for easy toggling

3. **ML Processor** (`backend/app/services/ml_processor.py`)

   - Updated to use UnifiedCounter
   - Tracking enabled by default

4. **API Endpoints** (`backend/app/api/v1/endpoints/yolo.py`)
   - `POST /api/v1/yolo/track` - Detection with tracking
   - `POST /api/v1/yolo/reset_tracker` - Reset tracker state

### ✅ Frontend (Complete)

1. **WebcamCounter** (`frontend/src/WebcamCounter.js`)
   - Added YOLO model option
   - Tracking toggle checkbox
   - Unique count display
   - Updated WebSocket handler for tracking data

## How to Run

### 1. Start Backend

```bash
cd backend
python run.py
```

### 2. Start Frontend

```bash
cd frontend
npm start
```

### 3. Test Tracking

Open browser at `http://localhost:3000`:

1. Select "🎥 Live Webcam" mode
2. Choose "YOLO (Detection + Tracking)" model
3. Check "Enable Tracking"
4. Click "Start Streaming"

### 4. Test API Directly

```bash
cd scripts
python test_tracking.py
```

## Response Format

### `/track` Endpoint Response

```json
{
  "count": 5,
  "unique_count": 12,
  "tracks": [
    {
      "id": 1,
      "box": [100, 200, 50, 80],
      "position": [125, 240],
      "state": "TRACKED"
    }
  ],
  "annotated_image": "base64_encoded_image"
}
```

## Key Features

### Tracking Capabilities

- ✅ Persistent track IDs across frames
- ✅ Unique person count (total seen)
- ✅ Current frame count (currently visible)
- ✅ Trajectory visualization
- ✅ Track state management

### Models Supported

- ✅ YOLO (with tracking)
- ✅ CSRNet (density map only)
- ✅ MCNN (density map only)
- ✅ TMTB/VMamba (density map only)

## Testing

### Manual Testing

1. Use webcam interface
2. Test with static images via `/track` endpoint
3. Test video tracking with `test_tracking.py`

### Automated Testing

```bash
cd ml
pytest tests/yolo/test_tracking.py -v
```

**Note**: Tests require sample data in `data/` folder.

## Next Steps

### Immediate (Optional)

1. Add trajectory visualization to frontend
2. Add track history display
3. Create video upload with tracking

### Future Enhancements

1. PedPy integration for density/flow metrics
2. Homography transformation for world coordinates
3. Multi-class tracking (vehicles + pedestrians)
4. Groq AI insights integration
5. Save tracking results to database

## Configuration

### Enable/Disable Tracking

**Backend**: `backend/app/services/ml_processor.py`

```python
ml_processor = MLProcessor(
    model_type='yolo',
    enable_tracking=True  # Set to False to disable
)
```

**Frontend**: Use tracking toggle checkbox

### Adjust Tracking Parameters

**File**: `ml/src/models/tracking/kalman_tracker.py`

```python
class KalmanTracker:
    def __init__(
        self,
        max_lost=30,        # Frames before track deletion
        min_hits=3,          # Frames before track confirmed
        iou_threshold=0.3    # Matching threshold
    ):
```

## Files Modified

### New Files

- `ml/src/models/tracking/kalman_tracker.py`
- `ml/src/models/tracking/__init__.py`
- `ml/src/models/unified_counter.py`
- `scripts/test_tracking.py`

### Updated Files

- `backend/app/services/ml_processor.py`
- `backend/app/api/v1/endpoints/yolo.py`
- `frontend/src/WebcamCounter.js`

## Dependencies

### Python (add to requirements.txt)

```
filterpy>=1.4.5
scipy>=1.7.0
```

### Install

```bash
cd backend
pip install filterpy scipy
```

## Troubleshooting

### Import Errors

If you see import errors for `UnifiedCounter` or `KalmanTracker`:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/ml/src"
```

### Tracking Not Working

1. Check backend logs for errors
2. Verify YOLO model is selected
3. Ensure tracking toggle is enabled
4. Reset tracker with `/reset_tracker` endpoint

### WebSocket Issues

1. Check backend is running on port 8000
2. Verify WebSocket endpoint is correct
3. Check browser console for errors
