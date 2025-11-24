# CSRNet Integration - Visual Architecture & Component Map

## 1. Complete System Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          BROWSER (Frontend)                                │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ Page: Webcam.js                                                  │  │
│  │                                                                   │  │
│  │ ┌──────────────────────────────────────────────────────────────┐ │  │
│  │ │ SettingsSidebar Component                                  │ │  │
│  │ │ • Model Selection: ["csrnet", "yolo-nano", "yolo-small"] │ │  │
│  │ │ • Detection Threshold: 0.5                                │ │  │
│  │ │ • Enable Heatmap: Toggle                                 │ │  │
│  │ │ • Enable Tracking: Toggle                                │ │  │
│  │ │ • Start/Stop Buttons                                     │ │  │
│  │ └──────────────────────────────────────────────────────────────┘ │  │
│  │                                                                   │  │
│  │ ┌──────────────────────────────────────────────────────────────┐ │  │
│  │ │ Visualization Grid (4-Card Layout)                       │ │  │
│  │ │                                                           │ │  │
│  │ │  ┌──────────────────────┐  ┌──────────────────────┐    │ │  │
│  │ │  │ LiveFeedCard         │  │ HeatmapCard          │    │ │  │
│  │ │  │ ┌────────────────┐   │  │ ┌────────────────┐   │    │ │  │
│  │ │  │ │  Webcam Video  │   │  │ │  Density Map   │   │    │ │  │
│  │ │  │ │ [Count: 45]    │   │  │ │  (Heatmap)     │   │    │ │  │
│  │ │  │ │ [FPS: 8.3]     │   │  │ │                │   │    │ │  │
│  │ │  │ └────────────────┘   │  │ └────────────────┘   │    │ │  │
│  │ │  └──────────────────────┘  └──────────────────────┘    │ │  │
│  │ │                                                           │ │  │
│  │ │  ┌──────────────────────┐  ┌──────────────────────┐    │ │  │
│  │ │  │ GraphCard            │  │ MetricsCard          │    │ │  │
│  │ │  │ ┌────────────────┐   │  │ ┌────────────────┐   │    │ │  │
│  │ │  │ │ Count History  │   │  │ │ Inference: ... │   │    │ │  │
│  │ │  │ │ (Line Chart)   │   │  │ │ Frame: 150     │   │    │ │  │
│  │ │  │ │ Last 30 points │   │  │ │ Model: CSRNet  │   │    │ │  │
│  │ │  │ └────────────────┘   │  │ └────────────────┘   │    │ │  │
│  │ │  └──────────────────────┘  └──────────────────────┘    │ │  │
│  │ └──────────────────────────────────────────────────────────┘ │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│         │                                                              │  │
│         └──────────────────────┬─────────────────────────┬─────┐       │
└─────────────────────────────────┼─────────────────────────┼─────┼───────┘
                                  │                         │     │
                     WebSocket Send/Receive               │     │
                     {"frame": base64,                     │     │
                      "model": "csrnet",                   │     │
                      "heatmap": true,                     │     │
                      "tracking": false}                   │     │
                                  │                         │     │
┌─────────────────────────────────┼─────────────────────────┼─────┼───────┐
│ SERVER (Backend Python)          │                         │     │       │
│                                  ▼                         │     │       │
│  ┌────────────────────────────────────────────────────────┐ │   │       │
│  │ FastAPI Application (main.py)                         │ │   │       │
│  │                                                       │ │   │       │
│  │ ┌──────────────────────────────────────────────────┐ │ │   │       │
│  │ │ @app.websocket("/ws/count")                    │ │ │   │       │
│  │ │                                                │ │ │   │       │
│  │ │ 1. Receive: frame + model_type               │ │ │   │       │
│  │ │ 2. Decode base64 → PIL Image                │ │ │   │       │
│  │ │ 3. Route to model:                          │ │ │   │       │
│  │ │    if model_type == "csrnet":               │ │ │   │       │
│  │ │       ↓                                      │ │ │   │       │
│  │ └───────────┬──────────────────────────────────┘ │ │   │       │
│  │             │                                    │ │   │       │
│  └─────────────┼────────────────────────────────────┘ │ │   │       │
│                │                                      │ │   │       │
│  ┌─────────────▼────────────────────────────────────┐ │ │   │       │
│  │ CSRNet Model (ml/src/models/csrnet/)            │ │ │   │       │
│  │                                                 │ │ │   │       │
│  │ ┌──────────────────────────────────────────┐   │ │ │   │       │
│  │ │ csrnet_api.predict(image, source="webcam")  │ │ │   │       │
│  │ │                                           │   │ │ │   │       │
│  │ │ • Load model checkpoint (csrnet.pth)    │   │ │ │   │       │
│  │ │ • Preprocess image (640x480, normalize) │   │ │ │   │       │
│  │ │ • Run inference on GPU/CPU              │   │ │ │   │       │
│  │ │ • Extract count from density map        │   │ │ │   │       │
│  │ │ • Optional: Generate heatmap            │   │ │ │   │       │
│  │ │                                           │   │ │ │   │       │
│  │ │ Return: {                               │   │ │ │   │       │
│  │ │   count: 45,                            │   │ │ │   │       │
│  │ │   inference_time_ms: 125.5,             │   │ │ │   │       │
│  │ │   device: "cuda"                        │   │ │ │   │       │
│  │ │ }                                        │   │ │ │   │       │
│  │ └──────────────────────────────────────────┘   │ │ │   │       │
│  └────────────────┬─────────────────────────────────┘ │ │   │       │
│                   │                                    │ │   │       │
│  ┌────────────────▼──────────────────────────────┐    │ │   │       │
│  │ Build Response JSON                          │    │ │   │       │
│  │ {                                            │    │ │   │       │
│  │   "success": true,                           │    │ │   │       │
│  │   "model": "csrnet",                         │    │ │   │       │
│  │   "count": 45,                               │    │ │   │       │
│  │   "fps": 8.3,                                │    │ │   │       │
│  │   "inference_time_ms": 125.5,                │    │ │   │       │
│  │   "frame_number": 150,                       │    │ │   │       │
│  │   "heatmap": "data:image/jpeg;base64,..."   │    │ │   │       │
│  │ }                                            │    │ │   │       │
│  └────────────────┬──────────────────────────────┘    │ │   │       │
│                   │                                    │ │   │       │
│                   └────────────────────────────────────┘─┼───┼────┐  │
│                           WebSocket Send               │   │    │  │
│                                                        │   │    │  │
└────────────────────────────────────────────────────────┘───┼────┼──┘
                                                             │    │
                                        Frontend Receives ◄──┘    │
                                        Updates State:           │
                                        • setResults()            │
                                        • setFps()                │
                                        • setCountHistory()       │
                                        • setHeatmapImage()       │
                                                                  │
                                        Re-render Triggered ◄─────┘
                                        Cards Update Display
```

---

## 2. Component Hierarchy & Data Flow

```
Webcam.js (Main Component)
│
├─ State Management (20+ variables)
│  ├─ isStreaming
│  ├─ results (full backend response)
│  ├─ fps
│  ├─ frameCount
│  ├─ countHistory (last 30 counts)
│  ├─ heatmapImage
│  ├─ selectedModel ("csrnet", "yolo-nano", etc.)
│  ├─ enableTracking
│  ├─ enableHeatmap
│  └─ ... (10+ more)
│
├─ WebSocket Connection & Loop
│  ├─ connectWebSocket() → ws://localhost:8000/ws/count
│  ├─ captureAndSendFrame() → Every 100ms
│  │  ├─ canvas.toDataURL("image/jpeg", 0.8)
│  │  └─ ws.send({frame, model, tracking, heatmap, threshold})
│  │
│  └─ ws.onmessage → Data Received
│     ├─ setResults(data)
│     ├─ setFps(data.fps)
│     ├─ setCountHistory([...prev, {time, count}])
│     └─ setHeatmapImage(data.heatmap) if enabled
│
├─ Render JSX
│  │
│  ├─ SettingsSidebar (all state setters passed)
│  │  ├─ Model Selector
│  │  ├─ Detection Threshold Slider
│  │  ├─ Feature Toggles
│  │  ├─ Display Options
│  │  ├─ Start/Stop Buttons
│  │  └─ Status Display
│  │
│  └─ Visualization Grid (4 Cards)
│     │
│     ├─ LiveFeedCard
│     │  ├─ Props: videoRef, canvasRef, results, fps, ...
│     │  ├─ Displays: Video + Count Overlay + Trajectory
│     │  └─ Updates: Every frame
│     │
│     ├─ HeatmapCard
│     │  ├─ Props: heatmapImage, enableHeatmap, ...
│     │  ├─ Displays: Density Heatmap (if available)
│     │  └─ Updates: Every frame (if enabled)
│     │
│     ├─ GraphCard
│     │  ├─ Props: countHistory, isStreaming, ...
│     │  ├─ Displays: Count over time line chart
│     │  └─ Updates: Every frame (adds to history)
│     │
│     └─ MetricsCard
│        ├─ Props: results, enableTracking, ...
│        ├─ Displays: Inference time, model, stats
│        └─ Updates: Every frame
```

---

## 3. Message Flow Diagram

```
TIME ↓

Frame 1:
Frontend  → [Base64 Frame #1, model: "csrnet", heatmap: true] → Backend
          ← [Count: 42, FPS: 10, InferenceTime: 125ms] ← Backend
          → Update State: results, countHistory, etc.
          → Re-render Cards: Show count 42, add to graph

Frame 2:
Frontend  → [Base64 Frame #2, model: "csrnet", heatmap: true] → Backend
          ← [Count: 43, FPS: 8.3, InferenceTime: 130ms] ← Backend
          → Update State: results, countHistory, etc.
          → Re-render Cards: Show count 43, add to graph

Frame 3:
Frontend  → [Base64 Frame #3, model: "csrnet", heatmap: true] → Backend
          ← [Count: 45, FPS: 7.9, InferenceTime: 120ms, Heatmap: "data:..."] ← Backend
          → Update State: results, countHistory, heatmapImage
          → Re-render Cards: All 4 cards update with new data

... (continuous loop every 100ms)
```

---

## 4. State Update Cascade

```
Backend Response Received
    ↓
ws.onmessage handler triggered
    ↓
    ├─→ setResults(data)
    │   ├─ LiveFeedCard re-renders
    │   └─ MetricsCard re-renders
    │
    ├─→ setFps(data.fps)
    │   └─ LiveFeedCard re-renders
    │
    ├─→ setCountHistory([...prev, {time: Date.now(), count: data.count}])
    │   └─ GraphCard re-renders & plots new point
    │
    └─→ setHeatmapImage(data.heatmap) [conditional]
        └─ HeatmapCard re-renders & displays new heatmap

Result: UI updates in ~50-100ms after backend response
```

---

## 5. File Organization Map

```
Frontend
├─ pages/
│  └─ Webcam.js ⭐ MAIN PAGE
│     ├─ Imports: Visualization components
│     ├─ State: 20+ variables
│     ├─ WebSocket: Connection & message handling
│     └─ Render: SettingsSidebar + 4 cards
│
├─ components/
│  ├─ Nav/
│  │  └─ Nav.js
│  │
│  ├─ Visualization/ ⭐ MODULAR COMPONENTS
│  │  ├─ index.js (barrel export)
│  │  ├─ LiveFeedCard.js
│  │  ├─ HeatmapCard.js
│  │  ├─ GraphCard.js
│  │  ├─ MetricsCard.js
│  │  ├─ SettingsSidebar.js
│  │  ├─ VisualizationCards.css
│  │  └─ SettingsSidebar.css
│  │
│  ├─ Heatmap/
│  │  └─ HeatmapOverlay.js
│  │
│  ├─ CountDisplay.js
│  ├─ Trajectory/
│  │  └─ TrajectoryCanvas.js
│  │
│  └─ AdvancedMetrics.js
│
└─ styles/
   ├─ WebcamPage.css
   └─ WebcamCounterNew.css

Backend
├─ app/
│  ├─ main.py ⭐ WEBSOCKET HANDLER & ROUTING
│  │  └─ @app.websocket("/ws/count")
│  │     ├─ Receive frame + settings
│  │     ├─ Route to appropriate model
│  │     └─ Send response
│  │
│  └─ api/v1/endpoints/
│     ├─ csrnet.py ⭐ CSRNET ENDPOINTS
│     │  ├─ GET /health
│     │  ├─ POST /count
│     │  └─ POST /webcam
│     │
│     ├─ yolo.py
│     ├─ tmtb.py
│     └─ ... (other models)
│
└─ config/
   └─ config.yaml

ML (Model Code)
├─ src/
│  └─ models/
│     └─ csrnet/ ⭐ CSRNET MODEL
│        ├─ csrnet.py (model definition)
│        ├─ api.py ⭐ INFERENCE API
│        │  ├─ get_model()
│        │  ├─ get_preprocessor()
│        │  ├─ generate_heatmap()
│        │  └─ predict() ← MAIN INFERENCE FUNCTION
│        │
│        └─ checkpoints/
│           └─ csrnet.pth (model weights)
```

---

## 6. Data Type Transformations

```
Webcam Stream (Video)
    ↓ canvas.toDataURL("image/jpeg", 0.8)
Base64 String (~92KB per frame)
    ↓ JSON.stringify()
JSON String
    ↓ WebSocket.send()
Network Transmission
    ↓ Backend receives
String
    ↓ base64.b64decode()
Bytes
    ↓ BytesIO()
File-like Object
    ↓ PIL.Image.open()
PIL Image (RGB)
    ↓ CSRNet Preprocessing
Preprocessed Tensor (torch.Tensor)
    ↓ Model Forward Pass (GPU/CPU)
Density Map Tensor
    ↓ sum().item()
Float: 45.23
    ↓ round()
Integer: 45
    ↓ JSON Response
{"count": 45, "fps": 8.3, ...}
    ↓ WebSocket.send()
Network Transmission
    ↓ Frontend receives
JSON String
    ↓ JSON.parse()
JavaScript Object
    ↓ setResults(data)
React State
    ↓ Component Re-render
    ├─ LiveFeedCard: Shows count "45"
    ├─ GraphCard: Plots point (time, 45)
    ├─ MetricsCard: Displays "Count: 45"
    └─ HeatmapCard: Shows density map
```

---

## 7. Critical Connection Points

### Point A: Backend Model Loading

```python
# backend/app/main.py
try:
    from models.csrnet import api as csrnet_api  ✅
    logger.info("✅ CSRNet API loaded successfully")
except ImportError as e:
    logger.warning(f"Could not import CSRNet: {e}")
    csrnet_api = None  ❌
```

### Point B: Frame Routing

```python
# backend/app/main.py:270
if model_type.lower() in yolo_model_map:
    result = yolo_api.predict(...)
elif model_type.lower() == "tmtb":
    result = tmtb_api.predict(...)
else:
    result = csrnet_api.predict(image, source="webcam")  ✅ CSRNET DEFAULT
    model_name = "CSRNet"
```

### Point C: Response Building

```python
# backend/app/main.py:278-292
response = {
    "success": True,
    "model": "csrnet",  ✅
    "count": result.get("count", result.get("rounded_count", 0)),  ✅
    "fps": 1000 / result["inference_time_ms"] if result.get("inference_time_ms", 0) > 0 else 0,  ✅
    ...
}
await websocket.send_json(response)  ✅ SEND BACK TO FRONTEND
```

### Point D: Frontend Reception

```javascript
// frontend/src/pages/Webcam.js:92
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);  ✅

    if (data.success) {
        setResults(data);  ✅ STORE ALL DATA
        setFps(data.fps || 0);  ✅ EXTRACT FPS
        setCountHistory(prev => [  ✅ UPDATE HISTORY
            ...prev,
            { time: Date.now(), count: data.count || 0 }
        ]);
    }
};
```

### Point E: Component Consumption

```javascript
// frontend/src/components/Visualization/LiveFeedCard.js
function LiveFeedCard({ results, fps, ... }) {
    return (
        <CountDisplay
            results={results}  ✅ PASS RESULTS
            fps={fps}  ✅ PASS FPS
        />
    );
}
```

---

## 8. Summary

```
✅ Data flows smoothly from CSRNet model → Backend → WebSocket → Frontend
✅ State properly managed in Webcam.js
✅ Components properly consume state
✅ Re-renders happen efficiently on each update
✅ Error handling on both backend and frontend
✅ All connections verified and documented
```
