# Previous Implementation Analysis (V1/V2)

## Architecture Overview

### Current System Components

#### 1. Backend (`backend/`)

- **Framework:** FastAPI
- **Main Components:**
  - `app/main.py` - API endpoints
  - `app/api/` - Route handlers
  - `app/services/` - Business logic
  - `app/camera/` - Camera/video handling

#### 2. ML Models (`ml/src/models/`)

```
models/
├── csrnet/         # Crowd density estimation (CNN-based)
├── mcnn/           # Multi-column CNN for counting
├── tmtb/           # Transformer model
└── yolo/           # YOLOv8 object detection
    └── yolov8_counter.py
```

#### 3. Frontend (`frontend/`)

- **Framework:** React
- **Components:**
  - `WebcamCounter.js` - Live webcam counting
  - Stream-based video processing
  - Real-time count display

### Current Workflow

```
┌─────────────┐
│   Frontend  │ (React)
│  Webcam UI  │
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────┐
│   Backend   │ (FastAPI)
│  API Server │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  ML Models  │
│ CSRNet/YOLO │
└─────────────┘
```

### Key Features (V2)

#### 1. **CSRNet Model**

- **Purpose:** Density map generation
- **Input:** Image (any size)
- **Output:** Density map → count estimation
- **Strengths:** Works well in crowded scenes
- **Limitations:** No individual tracking

**Location:** `ml/src/models/csrnet/`

```python
class CSRNet:
    def predict(self, image):
        # Generate density map
        density_map = self.model(image)
        count = density_map.sum()
        return count, density_map
```

#### 2. **YOLO Counter (V2)**

- **Purpose:** Person detection and counting
- **Input:** Image/frame
- **Output:** Bounding boxes, count
- **Strengths:** Individual detection, fast
- **Limitations:** No persistence across frames

**Location:** `ml/src/models/yolo/yolov8_counter.py`

```python
class YOLOv8Counter:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)
        self.conf_threshold = 0.25

    def predict(self, image):
        results = self.model(image)
        # Filter person class (0)
        boxes = results[0].boxes
        person_boxes = boxes[boxes.cls == 0]
        count = len(person_boxes)
        return count, person_boxes
```

#### 3. **API Endpoints (Current)**

**File:** `backend/app/api/`

```python
# Existing endpoints
POST /api/predict        # Single image prediction
POST /api/video/upload   # Video upload for processing
GET  /api/stream/webcam  # Webcam stream
POST /api/batch          # Batch processing
```

### Limitations of V2

| Issue                      | Impact                          | V3 Solution               |
| -------------------------- | ------------------------------- | ------------------------- |
| **No Tracking**            | Can't follow individuals        | ✅ Kalman filter tracking |
| **Frame-by-frame**         | Lost identity between frames    | ✅ Persistent track IDs   |
| **Image coordinates only** | No real-world metrics           | ✅ Homography mapping     |
| **Count only**             | No velocity, density analysis   | ✅ PedPy integration      |
| **Pedestrians only**       | Can't analyze mixed traffic     | ✅ Multi-class tracking   |
| **No trajectory data**     | Can't analyze movement patterns | ✅ Trajectory storage     |

### Data Flow (V2)

```python
# Current prediction flow
def process_frame(frame):
    # 1. Preprocess
    preprocessed = preprocess(frame)

    # 2. Model inference
    if model == "csrnet":
        density_map = csrnet.predict(preprocessed)
        count = density_map.sum()
    elif model == "yolo":
        count, boxes = yolo.predict(preprocessed)

    # 3. Return results
    return {
        "count": count,
        "timestamp": now()
    }
```

### Configuration (V2)

**File:** `backend/config.yaml`

```yaml
models:
  csrnet:
    checkpoint: "ml/checkpoints/csrnet.pth"
    device: "cuda"

  yolo:
    model: "yolov8n.pt"
    conf_threshold: 0.25
    iou_threshold: 0.45

camera:
  resolution: [1280, 720]
  fps: 30
```

### Testing Approach (V2)

**Location:** `ml/tests/`

- Jupyter notebooks for model validation
- No automated test suite for video/image testing
- Manual testing only

```
ml/tests/
├── 5-csrnet-check.ipynb      # CSRNet validation
├── 11-webcam.ipynb            # Webcam testing
└── test_device_manager.py     # Device utils
```

### Storage Structure (V2)

```
data/                          # ❌ Not well organized
backend/static/hls/           # HLS video chunks
logs/                         # Application logs
ml/checkpoints/              # Model checkpoints
  ├── csrnet.pth
  └── jhu_5.pth
```

### Dependencies (V2)

**Key Libraries:**

- `torch` - PyTorch models
- `ultralytics` - YOLOv8
- `opencv-python` - Video processing
- `fastapi` - API server
- `react` - Frontend

## What Works Well (Keep These)

✅ **FastAPI Backend** - Solid, fast, well-structured  
✅ **React Frontend** - Good UI/UX  
✅ **CSRNet Model** - Accurate for density estimation  
✅ **YOLO Integration** - Fast person detection  
✅ **Configuration System** - Flexible config.yaml  
✅ **Webcam Streaming** - Real-time processing works

## What Needs Enhancement (V3 Addresses)

⚠️ **Tracking** - Add persistent tracking  
⚠️ **Analytics** - Add speed, density, trajectory analysis  
⚠️ **World Coordinates** - Add real-world measurements  
⚠️ **Multi-object** - Support vehicles, bicycles  
⚠️ **Testing** - Add comprehensive test suite  
⚠️ **Data Management** - Organize data/ folder properly

---

**Next:** See [NEW_FEATURES.md](./NEW_FEATURES.md) for V3 capabilities
