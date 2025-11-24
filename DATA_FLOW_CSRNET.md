# CSRNet Data Flow Architecture - Backend to Frontend

## Overview

Complete data flow for CSRNet (and other crowd counting models) from backend API through frontend visualization components.

---

## 1. BACKEND LAYER - API Endpoints

### 1.1 CSRNet API Endpoint

**File:** `backend/app/api/v1/endpoints/csrnet.py`

**Available Endpoints:**

```
GET  /api/v1/csrnet/health          → Health check
POST /api/v1/csrnet/count           → Image file upload for counting
POST /api/v1/csrnet/predict         → Alias for count endpoint
POST /api/v1/csrnet/webcam          → Webcam frame counting
```

**Response Format:**

```json
{
  "status": "success",
  "count": 45,
  "raw_count": 45.2,
  "inference_time_ms": 120.5,
  "device": "cuda",
  "original_size": [640, 480],
  "processed_size": [640, 480]
}
```

### 1.2 CSRNet ML Model

**File:** `ml/src/models/csrnet/api.py`

**Model API Functions:**

- `get_model(checkpoint_path)` → Loads CSRNet model from checkpoint
- `get_preprocessor()` → Returns image preprocessing pipeline
- `predict(image, source, return_density_map)` → Runs inference and returns:
  ```python
  {
    "count": float,
    "rounded_count": int,
    "inference_time_ms": float,
    "device": str,
    "density_map_shape": tuple,
    "original_size": tuple,
    "processed_size": tuple,
    "source": str
  }
  ```

**Key Features:**

- Config-driven resizing based on source type (webcam vs image vs video)
- CUDA/CPU device detection
- Optional density map generation for heatmaps

---

## 2. BACKEND WEBSOCKET HANDLER - Real-time Processing

**File:** `backend/app/main.py` - `@app.websocket("/ws/count")`

### 2.1 WebSocket Data Reception

```javascript
// Frontend sends:
{
  "frame": "data:image/jpeg;base64,...",  // Base64 encoded frame
  "model": "csrnet",                      // Model selection
  "tracking": false,                      // Enable tracking
  "heatmap": false,                       // Enable heatmap
  "threshold": 0.5                        // Detection threshold
}
```

### 2.2 Model Selection Logic

```python
if model_type.lower() in yolo_model_map:
    # YOLO object detection
    result = yolo_api.predict(...)

elif model_type.lower() == "tmtb":
    # TMTB/VMamba density estimation
    result = tmtb_api.predict(...)

else:
    # CSRNet - default density estimation
    result = csrnet_api.predict(image, source="webcam")
    model_name = "CSRNet"
```

### 2.3 WebSocket Response to Frontend

```javascript
{
  "success": true,
  "model": "csrnet",
  "count": 45,
  "inference_time_ms": 120.5,
  "frame_number": 125,
  "fps": 8.3,
  "boxes": [],                    // Empty for density models
  "heatmap": "data:image/jpeg;base64,..."  // If requested
}
```

---

## 3. FRONTEND WEBSOCKET CONNECTION

**File:** `frontend/src/pages/Webcam.js`

### 3.1 Connection Establishment

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/count");
```

### 3.2 Message Reception (onmessage handler)

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.success) {
    // Store raw results
    setResults(data);

    // Extract metrics
    setFps(data.fps || 0);
    setFrameCount(data.frame_number || 0);

    // Update count history for graph
    setCountHistory((prev) => {
      const newHistory = [
        ...prev,
        { time: Date.now(), count: data.count || 0 },
      ];
      return newHistory.slice(-30); // Keep last 30 points
    });

    // Update heatmap if received
    if (enableHeatmap && data.heatmap) {
      setHeatmapImage(data.heatmap);
    }
  }
};
```

### 3.3 Frame Capture & Sending

```javascript
const captureAndSendFrame = useCallback(() => {
  const frameData = canvas.toDataURL("image/jpeg", 0.8); // Compress to 80%

  wsRef.current.send(
    JSON.stringify({
      frame: frameData,
      model: selectedModel, // "csrnet" or other
      tracking: enableTracking,
      heatmap: enableHeatmap,
      threshold: detectionThreshold,
    })
  );
}, [selectedModel, enableTracking, enableHeatmap, detectionThreshold]);
```

---

## 4. STATE MANAGEMENT - Webcam.js Component State

**Key State Variables:**

```javascript
// Raw data from backend
const [results, setResults] = useState(null); // Full response
const [fps, setFps] = useState(0); // Frames per second
const [frameCount, setFrameCount] = useState(0); // Frame number
const [uniqueCount, setUniqueCount] = useState(0); // Tracking count

// Visualization data
const [countHistory, setCountHistory] = useState([]); // Last 30 counts: [{time, count}]
const [heatmapImage, setHeatmapImage] = useState(null); // Base64 heatmap

// Control settings
const [selectedModel, setSelectedModel] = useState("yolo-nano");
const [enableTracking, setEnableTracking] = useState(false);
const [enableHeatmap, setEnableHeatmap] = useState(false);
const [detectionThreshold, setDetectionThreshold] = useState(0.5);
const [showLiveCount, setShowLiveCount] = useState(true);
const [showHeatmap, setShowHeatmap] = useState(true);
const [showGraph, setShowGraph] = useState(true);
const [showMetrics, setShowMetrics] = useState(true);
```

---

## 5. VISUALIZATION CARD COMPONENTS

### 5.1 LiveFeedCard.js

**Consumes:**

- `videoRef` - Direct access to video element
- `results.count` - Current count from detection
- `fps` - Frames per second
- `enableTracking` - Show trajectory overlay
- `uniqueCount` - Tracking count (if enabled)

**Displays:**

- Live video stream (real-time)
- Count overlay on video
- Trajectory paths (if tracking enabled)
- FPS indicator
- Count display

**Component Structure:**

```javascript
<div className="viz-card live-count-card">
  <video ref={videoRef} autoPlay muted />
  <canvas ref={canvasRef} style={{ display: "none" }} />
  {enableTracking && <TrajectoryCanvas />}
  {isStreaming && <CountDisplay results={results} fps={fps} />}
</div>
```

### 5.2 HeatmapCard.js

**Consumes:**

- `heatmapImage` - Base64 encoded heatmap from backend
- `enableHeatmap` - Toggle visibility
- `modelType` - Display model name

**Displays:**

- Density/detection heatmap visualization
- Colored overlay of detection intensity
- Placeholder when heatmap not available

**Component Structure:**

```javascript
<div className="viz-card heatmap-card">
  {isStreaming && enableHeatmap && heatmapImage ? (
    <HeatmapOverlay heatmapImage={heatmapImage} />
  ) : (
    <div className="placeholder">Enable heatmap in settings</div>
  )}
</div>
```

### 5.3 GraphCard.js

**Consumes:**

- `countHistory` - Array of {time, count} objects (last 30)
- `isStreaming` - Show/hide placeholder

**Displays:**

- Line chart of count over time
- Statistics: Current, Average, Peak counts
- Data points count

**Component Structure:**

```javascript
<div className="viz-card graph-card">
  {isStreaming && countHistory.length > 0 ? (
    <>
      <SimpleChart data={countHistory} />
      <GraphStats stats={{ current, average, peak }} />
    </>
  ) : (
    <Placeholder />
  )}
</div>
```

### 5.4 MetricsCard.js

**Consumes:**

- `results.inference_time_ms` - Processing time
- `results.frame_number` - Current frame
- `results.advanced_metrics` - Tracking metrics
- `enableTracking` - Show tracking data

**Displays:**

- Inference timing metrics
- Model information
- Tracking data (if available)
- Speed statistics
- Active tracks table

**Component Structure:**

```javascript
<div className="viz-card metrics-card">
  {isStreaming && enableTracking && results.advanced_metrics ? (
    <AdvancedMetrics metrics={results.advanced_metrics} />
  ) : isStreaming && results ? (
    <BasicMetrics
      inference={results.inference_time_ms}
      frame={results.frame_number}
    />
  ) : (
    <Placeholder />
  )}
</div>
```

### 5.5 SettingsSidebar.js

**Consumes:**

- All state setters from Webcam.js

**Provides:**

- Model selection dropdown
- Detection threshold slider
- Feature toggles (tracking, heatmap)
- Display options checkboxes
- Start/Stop streaming buttons
- Status information display

---

## 6. COMPLETE DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Python)                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ WebSocket Handler (/ws/count)                           │  │
│  │ ├─ Receive frame + model type + settings               │  │
│  │ ├─ Select appropriate model (CSRNet/YOLO/TMTB)        │  │
│  │ ├─ Call csrnet_api.predict(frame, source="webcam")    │  │
│  │ └─ Return response with count, fps, etc.              │  │
│  └────────┬──────────────────────────────────────────────────┘  │
│           │                                                       │
│  ┌────────▼──────────────────────────────────────────────────┐  │
│  │ CSRNet Model (ml/src/models/csrnet/)                    │  │
│  │ ├─ Load model checkpoint                                │  │
│  │ ├─ Preprocess image (resize, normalize)                │  │
│  │ ├─ Run inference on GPU/CPU                            │  │
│  │ └─ Return count + inference_time + device             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │ WebSocket
                            │ JSON Response
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Webcam.js (Main Page Component)                         │  │
│  │ ├─ WebSocket Connection & Message Handler              │  │
│  │ ├─ State: results, fps, countHistory, heatmapImage    │  │
│  │ ├─ State: model selection, thresholds, toggles        │  │
│  │ └─ Webcam access & frame capture loop (100ms)         │  │
│  └──────────────────────────────────────────────────────────┘  │
│           │                           │
│           │ Pass props              │ Pass props
│           ▼                          ▼
│  ┌────────────────────┐  ┌──────────────────────┐
│  │ SettingsSidebar    │  │ Visualization Grid   │
│  │ ├─ Model selector  │  │ ├─ LiveFeedCard     │
│  │ ├─ Thresholds      │  │ ├─ HeatmapCard      │
│  │ ├─ Toggles         │  │ ├─ GraphCard        │
│  │ └─ Start/Stop      │  │ └─ MetricsCard      │
│  └────────────────────┘  └──────────────────────┘
│                                   │
│                          ┌────────┴────────┬────────────┬──────────┐
│                          │                 │            │          │
│                    ┌─────▼──┐        ┌────▼───┐   ┌───▼────┐  ┌──▼────┐
│                    │Live    │        │Heatmap │   │Graph   │  │Metrics│
│                    │Feed    │        │        │   │        │  │       │
│                    │Video + │        │Base64  │   │Count   │  │Track  │
│                    │Count   │        │Image   │   │History │  │Data   │
│                    └────────┘        └────────┘   └────────┘  └───────┘
│
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. DATA TYPES AND FLOW

### 7.1 Image Frame Flow

```
Webcam Video Stream
  ↓
Canvas Capture (640x480)
  ↓
toDataURL("image/jpeg", 0.8)  [80% compression]
  ↓
Base64 String
  ↓
WebSocket Send
  ↓
Backend JSON.loads()
  ↓
BytesIO → PIL Image
  ↓
CSRNet Preprocessing
  ↓
Tensor Input
  ↓
GPU/CPU Inference
  ↓
Density Map Output
  ↓
Count Extraction
  ↓
JSON Response
  ↓
WebSocket Receive
  ↓
Frontend State Update
```

### 7.2 Count Data Flow

```
Backend: result.get("count", 45)
  ↓
Response: "count": 45
  ↓
Frontend: data.count
  ↓
setResults(data)  [stores full response]
  ↓
countHistory update: [...prev, {time, count: 45}]
  ↓
Live Feed: Shows "45" overlay
  ↓
Graph: Plots point (time, 45)
  ↓
Metrics: Displays count stats
```

### 7.3 Heatmap Data Flow

```
Backend: heatmap enabled
  ↓
CSRNet generates density map
  ↓
generate_heatmap() function:
  ├─ Normalize density map (0-255)
  ├─ Apply colormap (COLORMAP_JET)
  ├─ Blend with original image (40% img, 60% heatmap)
  └─ Return BGR numpy array
  ↓
cv2.imencode('.jpg') → buffer
  ↓
base64.encode(buffer)
  ↓
Response: "heatmap": "data:image/jpeg;base64,..."
  ↓
Frontend: data.heatmap
  ↓
setHeatmapImage(data.heatmap)
  ↓
HeatmapCard: <img src={heatmapImage} />
```

---

## 8. ERROR HANDLING

### Backend Error Handling

```python
try:
    result = csrnet_api.predict(image, source="webcam")
except Exception as e:
    logger.error(f"Prediction error: {e}")
    await websocket.send_json({
        "success": False,
        "error": f"Prediction failed: {str(e)}"
    })
```

### Frontend Error Handling

```javascript
ws.onerror = (error) => {
  console.error("WebSocket error:", error);
  setError("WebSocket connection error");
};

ws.onclose = () => {
  if (isStreaming) {
    setError("Connection lost. Please restart.");
  }
};

if (data.success) {
  // Process data
} else {
  console.error("Processing error:", data.error);
}
```

---

## 9. PERFORMANCE METRICS

**Frame Processing Loop:**

- Capture interval: 100ms (10 FPS target)
- Compression: 80% JPEG quality
- Backend inference: ~120-150ms (CSRNet)
- Total latency: ~200-250ms per frame

**Memory Usage:**

- Frame buffer: ~640x480x3 = ~923KB
- Base64 encoding adds ~33% overhead
- countHistory: 30 frames × minimal data = ~2KB

**Throughput:**

- 10 frames per second (configurable)
- ~92KB per frame (base64 encoded)
- ~920KB/s bandwidth (uncompressed)

---

## 10. INTEGRATION CHECKLIST

✅ Backend CSRNet API functional
✅ WebSocket handler receives frames
✅ Model selection logic implemented
✅ Frontend WebSocket connection established
✅ State management in Webcam.js
✅ Frame capture and sending loop
✅ LiveFeedCard displays results
✅ HeatmapCard displays heatmap
✅ GraphCard tracks count history
✅ MetricsCard shows statistics
✅ SettingsSidebar controls all settings
✅ Error handling on both sides
✅ Auto-model switching logic
✅ Tracking integration (YOLO + trajectory)
✅ Responsive UI layout

---

## 11. TESTING STEPS

1. **Backend Health Check:**

   ```bash
   curl http://localhost:8000/api/v1/csrnet/health
   ```

2. **WebSocket Connection:**

   - Open browser console
   - Navigate to webcam page
   - Check for "✅ WebSocket connected" message

3. **Frame Processing:**

   - Start streaming (click Start button)
   - Verify frames are being sent (check Network tab)
   - Monitor backend logs for inference times

4. **Visualization:**

   - Check LiveFeedCard shows real-time count
   - Verify GraphCard is plotting count history
   - Enable heatmap and verify display
   - Enable tracking and verify trajectory

5. **Auto-Switch:**
   - Enable auto-switch mode
   - Set threshold to 30
   - Verify model switches between CSRNet and YOLO

---

## 12. DEPLOYMENT NOTES

- Backend must be running on `localhost:8000`
- Frontend must connect to same backend
- CORS middleware configured for cross-origin access
- WebSocket timeout: Configure based on network conditions
- Model checkpoints must be available in `ml/checkpoints/`
