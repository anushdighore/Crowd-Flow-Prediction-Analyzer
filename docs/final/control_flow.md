# 🎮 CONTROL FLOW REPORT - Complete System Flow Diagrams

**Project:** Crowd Flow Prediction Analyzer  
**Generated:** November 25, 2025  
**Scope:** Frontend → Backend → ML Models → Response

---

## 📑 TABLE OF CONTENTS

1. [Complete System Control Flow](#complete-system-control-flow)
2. [Frontend Control Flow (React)](#frontend-control-flow-react)
3. [Backend Control Flow (FastAPI)](#backend-control-flow-fastapi)
4. [Model Pipeline Flows](#model-pipeline-flows)
5. [Data Path Flows (Broken & Working)](#data-path-flows-broken--working)
6. [Stop/Cleanup Sequence](#stopcleanup-sequence)

---

## 🎯 COMPLETE SYSTEM CONTROL FLOW

### High-Level System Architecture

```mermaid
graph TB
    subgraph UI["🖥️ FRONTEND (React)"]
        Auth["🔐 AuthContext<br/>isAuthenticated"]
        WebcamCtx["📹 WebcamContext<br/>State Management"]
        Pages["Pages:<br/>- Webcam.js<br/>- ExternalCamera.js<br/>- Image.js<br/>- Video.js"]
        Cards["Components:<br/>- CSRNetCard<br/>- HeatmapCard<br/>- YOLOUploader<br/>- etc."]
    end

    subgraph API["🌐 BACKEND (FastAPI main.py)"]
        CORS["✅ CORS Middleware<br/>localhost:3000|5173"]
        Router["🔀 GatedModelRouter<br/>Model Selection"]
        WS1["📡 /ws/count<br/>Webcam Streaming"]
        WS2["📡 /ws/external-camera<br/>IP Camera"]
        REST["🔗 REST Endpoints<br/>/api/v1/{model}/count"]
    end

    subgraph ML["🤖 ML LAYER (PyTorch)"]
        CSRNet["CSRNet<br/>Density Estimation"]
        TMTB["TMTB/VMamba<br/>Density Estimation"]
        YOLO["YOLO v8<br/>Object Detection"]
        UnifiedCounter["UnifiedCounter<br/>Tracking Engine"]
    end

    UI -->|WebSocket| API
    UI -->|HTTP REST| API
    API -->|Model Selection| Router
    Router -->|predict()| CSRNet
    Router -->|predict()| TMTB
    Router -->|predict()| YOLO
    YOLO -->|Optional| UnifiedCounter

    CSRNet -->|Density Map + Count| API
    TMTB -->|Density Map + Count| API
    YOLO -->|Boxes + Count| API
    UnifiedCounter -->|Tracks + Count| API

    API -->|Response JSON| UI
```

---

## 🖥️ FRONTEND CONTROL FLOW (React)

### App Entry Point & Provider Setup

```
App.js (ENTRY)
    ↓
<BrowserRouter>
    ↓
<WebcamProvider>  ← Creates WebcamContext
    ↓
<AppContent>
    ├─ <Routes>
    │  ├─ Route: "/login" → LoginPage
    │  ├─ Route: "/" → Dashboard
    │  ├─ Route: "/webcam" → Webcam.js ← MAIN FLOW
    │  ├─ Route: "/external-camera" → ExternalCameraPage
    │  ├─ Route: "/image" → Image.js (Upload)
    │  └─ Route: "/video" → Video.js (Upload)
    │
    └─ Conditional Rendering (if authenticated)
```

### WebcamContext Initialization

```javascript
WebcamProvider (frontend/src/context/WebcamContext.js)
    │
    ├─ STATE:
    │  ├─ isStreaming (boolean)
    │  ├─ selectedModel (string: "CSRNet"|"TMTB"|"YOLO-*")
    │  ├─ enableTracking (boolean)
    │  ├─ enableHeatmap (boolean) ← KEY FOR HEATMAP PIPELINE
    │  ├─ detectionThreshold (float: 0-1)
    │  ├─ count (number)
    │  ├─ fps (number)
    │  ├─ inferenceTime (number)
    │  ├─ results (object: raw backend response)
    │  ├─ heatmapImage (string: base64 or null)
    │  ├─ densityStats (object)
    │  └─ error (string | null)
    │
    ├─ REFS:
    │  ├─ videoRef → <video> element
    │  ├─ canvasRef → Canvas for frame capture
    │  ├─ streamRef → MediaStream from getUserMedia()
    │  ├─ intervalRef → Frame capture interval (100ms)
    │  └─ wsRef → WebSocket connection
    │
    └─ FUNCTIONS:
       ├─ connectWebSocket() → Promise
       ├─ startStreaming() → Opens webcam
       ├─ stopStreaming() → Stops webcam
       ├─ stopEverything() → CLEANUP
       └─ (WebSocket onmessage handler)
```

### Webcam.js Component Flow (WORKING PATH ✅)

```
Webcam.js Main Component Flow
│
├─ MOUNT EFFECT (Empty deps array - runs once on mount)
│  └─ Listen for WebSocket messages
│     └─ No immediate action
│
├─ RENDER
│  ├─ Header with title
│  ├─ Status Panel (displays:  status, FPS, inference_time, model)
│  └─ Results Section (if isStreaming)
│     ├─ CSRNetCard (displays results object as JSON)
│     ├─ Debug Info (shows: enableHeatmap, heatmapImage exists, length)
│     └─ Layout Grid (3 columns)
│
└─ USER INTERACTIONS
   │
   ├─ Start Button (StreamBtn)
   │  └─ Call: useWebcam().handleStartStreaming()
   │     └─ Context function that:
   │        1. navigator.mediaDevices.getUserMedia()
   │        2. Open <video> element
   │        3. Attach MediaStream to videoRef
   │        4. connectWebSocket()
   │        5. Set interval to capture frames every 100ms
   │        6. canvas.toDataURL('image/jpeg', 0.8) → Base64
   │        7. Send via WebSocket: {frame, model, heatmap: enableHeatmap, ...}
   │
   ├─ Stop Button
   │  └─ Call: stopEverything()
   │
   ├─ Model Selection Dropdown (RightMenu)
   │  └─ onChange → setSelectedModel(newModel)
   │     └─ WebSocket updated in next frame send
   │
   ├─ Heatmap Toggle (RightMenu)
   │  └─ onChange → setEnableHeatmap(value)
   │     └─ Sent in next frame: {frame, heatmap: value, ...}
   │
   └─ Tracking Toggle (RightMenu)
      └─ onChange → setEnableTracking(value)
```

### Context WebSocket Message Handler

```javascript
ws.onmessage = (event) => {
    data = JSON.parse(event.data)

    if (data.success) {
        // Update state
        setCount(data.count)
        setFps(data.fps)
        setInferenceTime(data.timing?.inference_ms)
        setResults(data)  ← Store entire response

        // CRITICAL: Heatmap extraction
        if (data.heatmap) {
            setHeatmapImage(data.heatmap)  ← base64 string
            console.log("🔥 Heatmap received, length:", data.heatmap.length)
        } else {
            console.log("⚠️ No heatmap in response")  ← BREAKPOINT
        }

        if (data.density_map_stats) {
            setDensityStats(data.density_map_stats)
        }

        setStatus(`${data.count} | FPS: ${data.fps}`)
    } else {
        setError(data.error)  ← Error handling
    }
}
```

### Frontend Frame Capture & Send Loop (100ms interval)

```javascript
setInterval(() => {
    if (!canvasRef.current || !videoRef.current || !wsRef.current) return

    // Capture frame
    const ctx = canvasRef.current.getContext('2d')
    ctx.drawImage(videoRef.current, 0, 0)
    const frameBase64 = canvasRef.current.toDataURL('image/jpeg', 0.8)

    // Build payload
    const payload = {
        frame: frameBase64,              ← data:image/jpeg;base64,/9j/4AAQ...
        model: selectedModel,            ← "CSRNet" | "TMTB" | "yolo-nano" | etc.
        tracking: enableTracking,        ← true | false
        heatmap: enableHeatmap,          ← true | false  [KEY PARAMETER]
        threshold: detectionThreshold    ← 0.5
    }

    // Send
    wsRef.current.send(JSON.stringify(payload))
}, 100)  ← Frames every 100ms = ~10 FPS capture rate
```

---

## 🔌 BACKEND CONTROL FLOW (FastAPI)

### Main.py WebSocket Handler: /ws/count

**Entry Point:** `backend/app/main.py:168`

```python
@app.websocket("/ws/count")
async def websocket_count(websocket: WebSocket):

    # 1. ACCEPT CONNECTION
    await websocket.accept()
    logger.info("✅ WebSocket connected for real-time counting")

    frame_number = 0

    # 2. MAIN MESSAGE LOOP
    while True:
        # 2a. Receive JSON payload from frontend
        data = await websocket.receive_json()

        # 2b. EXTRACT PARAMETERS (CRITICAL SECTION)
        frame_data = data.get("frame") or data.get("image")
        model_type = data.get("model", "csrnet")          ← Model selection
        enable_tracking = data.get("tracking", False)     ← Tracking flag
        return_heatmap = data.get("heatmap", False)       ← HEATMAP FLAG ← KEY!

        # 2c. DECODE FRAME
        if frame_data.startswith("data:image"):
            frame_data = frame_data.split(",")[1]         ← Remove prefix

        image_bytes = base64.b64decode(frame_data)
        image = Image.open(io.BytesIO(image_bytes))       ← PIL Image

        # 3. MODEL SELECTION ROUTING (3 paths)

        ┌─ PATH A: YOLO Model (Object Detection)
        │  if model_type.lower() in yolo_model_map:
        │      if enable_tracking:
        │          counter = get_tracking_counter(checkpoint)
        │          result = counter.predict(img_array, return_visualization=return_heatmap)
        │      else:
        │          result = yolo_api.predict(image, visualize=return_heatmap)
        │
        ├─ PATH B: TMTB Model (Density Estimation)
        │  elif model_type.lower() == "tmtb":
        │      result = tmtb_api.predict(image, source="webcam")
        │
        └─ PATH C: CSRNet Model (Density Estimation - DEFAULT)
           else:
               result = csrnet_api.predict(
                   image,
                   source="webcam",
                   return_density_map=return_heatmap  ← PASSED HERE
               )
               logger.info(f"🔍 CSRNet result keys: {list(result.keys())}")
               logger.info(f"return_heatmap={return_heatmap}, has_density_map={'density_map' in result}")

        # 4. INCREMENT FRAME COUNTER
        frame_number += 1

        # 5. BUILD RESPONSE OBJECT
        response = {
            "success": True,
            "model": model_name.lower(),
            "count": result.get("count", 0),
            "inference_time_ms": result.get("inference_time_ms", 0),
            "frame_number": frame_number,
            "fps": 1000 / result.get("inference_time_ms", 1)
        }

        # 6. MODEL-SPECIFIC RESPONSE ADDITIONS

        ┌─ If YOLO:
        │  response["boxes"] = result.get("boxes", [])
        │  response["num_detections"] = len(result.get("boxes", []))
        │  if result.get("boxes"):
        │      confidences = [box.get("confidence", 0) for box in result.get("boxes", [])]
        │      response["average_confidence"] = sum(confidences) / len(confidences)
        │
        │  # Heatmap for YOLO
        │  if return_heatmap and "annotated_image" in result:
        │      annotated_bgr = result["annotated_image"]
        │      _, buffer = cv2.imencode('.jpg', annotated_bgr)
        │      response["heatmap"] = f"data:image/jpeg;base64,{base64_encoded}"
        │
        ├─ If TRACKING enabled:
        │  response["unique_count"] = result.get("unique_count", response["count"])
        │  response["tracks"] = result.get("tracks", [])
        │  response["speed_stats"] = result.get("speed_stats", {})
        │  response["advanced_metrics"] = counter.get_advanced_metrics(...)
        │
        └─ CRITICAL HEATMAP SECTION (CSRNet/TMTB):
           if return_heatmap and "density_map" in result and model_type not in yolo_model_map:
               try:
                   logger.info(f"🔥 Generating heatmap for {model_type}")
                   heatmap_overlay = csrnet_api.generate_heatmap(
                       result["density_map"],
                       image
                   )
                   _, buffer = cv2.imencode('.jpg', heatmap_overlay)
                   img_base64 = base64.b64encode(buffer).decode()
                   response["heatmap"] = f"data:image/jpeg;base64,{img_base64}"
                   logger.info(f"✅ Heatmap generated, length: {len(img_base64)}")
               except Exception as e:
                   logger.error(f"❌ Heatmap generation failed: {e}")
           else:
               logger.info(f"⚠️ Heatmap NOT generated - return_heatmap={return_heatmap}, has_density_map={'density_map' in result}, model_type={model_type}")

        # 7. SEND RESPONSE
        await websocket.send_json(response)

    # 8. EXCEPTION HANDLING
except WebSocketDisconnect:
    logger.info("❌ WebSocket disconnected")
except Exception as e:
    logger.error(f"WebSocket error: {e}")
```

### External Camera WebSocket Handler: /ws/external-camera

**Entry Point:** `backend/app/main.py:374`

```python
@app.websocket("/ws/external-camera")
async def websocket_external_camera(websocket: WebSocket):

    # 1. Accept connection
    await websocket.accept()

    frame_number = 0
    camera_url = None
    model_type = "csrnet"

    while True:
        data = await websocket.receive_json()

        # 2. CONFIG MESSAGE HANDLING
        if "camera_url" in data:
            camera_url = data["camera_url"]
            model_type = data.get("model", "csrnet")
            enable_tracking = data.get("tracking", False)

            logger.info(f"📹 Camera URL set: {camera_url}, Model: {model_type}")

            await websocket.send_json({
                "success": True,
                "message": "Camera configured",
                "camera_url": camera_url
            })
            continue  ← Wait for next message

        # 3. FRAME REQUEST
        if data.get("action") == "get_frame":

            # 3a. Get frame from camera
            frame = await camera_client.get_frame(camera_url)

            if frame is None:
                await websocket.send_json({"success": False, "error": "Frame fetch failed"})
                continue

            # 3b. Convert to PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            # 3c. MODEL ROUTING (similar to /ws/count but with model_router)

            if enable_tracking and model_type in yolo_model_map:
                # Use UnifiedCounter with tracking
                result = counter.predict(img_array, return_visualization=True)
                heatmap_frame = result.get('annotated_image')

            else if model_router:
                # Use gated router
                result = model_router.predict(
                    pil_image,
                    model_type=model_type,
                    source="surveillance",
                    return_density_map=True,
                    return_boxes=(model_type in yolo_model_map)
                )

                # Generate heatmap via router
                if model_type in yolo_model_map:
                    if result.get('boxes') and len(result['boxes']) > 0:
                        heatmap_frame = model_router.generate_heatmap(
                            model_type, result, pil_image
                        )
                else:
                    heatmap_frame = model_router.generate_heatmap(
                        model_type, result, pil_image
                    )

            else:
                # Fallback to legacy
                result = csrnet_api.predict(pil_image, source="surveillance", return_density_map=True)
                heatmap_frame = None

            # 3d. Build response with encoded frames
            frame_number += 1

            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode()

            response_data = {
                "success": True,
                "model": model_name.lower(),
                "count": result.get("rounded_count", 0),
                "inference_time_ms": result.get("inference_time_ms", 0),
                "frame": f"data:image/jpeg;base64,{frame_base64}",
                "frame_number": frame_number
            }

            if heatmap_frame is not None:
                _, heatmap_buffer = cv2.imencode('.jpg', heatmap_frame)
                heatmap_base64 = base64.b64encode(heatmap_buffer).decode()
                response_data["heatmap"] = f"data:image/jpeg;base64,{heatmap_base64}"

            await websocket.send_json(response_data)
```

### REST API Endpoints

#### CSRNet Endpoint: POST /api/v1/csrnet/count

```python
@router.post("/count")
async def count(file: UploadFile = File(...)):
    # 1. Read uploaded file
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # 2. Predict (no heatmap by default)
    result = csrnet_api.predict(image, source="image", return_density_map=False)

    # 3. Build response
    response = {
        "status": "success",
        "count": result["rounded_count"],
        "raw_count": result["count"],
        "inference_time_ms": result["inference_time_ms"],
        "device": result["device"]
    }

    # 4. Optional heatmap (if return_heatmap query param = true)
    if return_heatmap and "density_map" in result:
        heatmap = csrnet_api.generate_heatmap(result["density_map"], image)
        _, buffer = cv2.imencode('.jpg', heatmap)
        response["heatmap"] = f"data:image/jpeg;base64,{base64_encoded}"

    return response
```

#### YOLO Endpoint: POST /api/v1/yolo/count

```python
@router.post("/count")
async def count(file: UploadFile = File(...)):
    # 1. Read file
    image = Image.open(io.BytesIO(await file.read()))

    # 2. Predict
    result = yolo_api.predict(image, visualize=True)

    # 3. Response with boxes
    response = {
        "status": "success",
        "count": result["rounded_count"],
        "boxes": result.get("boxes", []),
        "annotated_image": result.get("annotated_image")
    }

    return response
```

---

## 🤖 MODEL PIPELINE FLOWS

### CSRNet Inference Pipeline

```
ml/src/models/csrnet/api.py:predict()
│
├─ INPUT:
│  ├─ image: PIL.Image
│  ├─ checkpoint_path: optional
│  ├─ source: "image|webcam|video|surveillance"
│  └─ return_density_map: boolean ← KEY PARAMETER
│
├─ LOAD CONFIG
│  └─ config = load_csrnet_config()
│  └─ dims = config.preprocessing.get_dimensions(source)
│     └─ source="webcam" → (320, 240)
│     └─ source="image" → (640, 480)
│     └─ source="surveillance" → (320, 240)
│
├─ RESIZE IMAGE
│  └─ Maintain aspect ratio
│  └─ Limit to max_dimension
│  └─ Divisible by 8 (CSRNet requirement)
│
├─ GET MODEL & PREPROCESSOR
│  └─ model = get_model(checkpoint_path)  [Global cache]
│  └─ preprocessor = get_preprocessor()
│
├─ PREPROCESS
│  └─ normalize with ImageNet stats
│  └─ convert to tensor
│  └─ move to device (CPU/CUDA)
│
├─ INFERENCE
│  └─ with torch.no_grad():
│     └─ density_map = model(img_tensor)  ← OUTPUT: density map
│     └─ count = density_map.sum().item()
│
├─ OUTPUT:
│  ├─ count: float
│  ├─ rounded_count: int
│  ├─ inference_time_ms: float
│  ├─ device: str
│  ├─ original_size: tuple
│  ├─ processed_size: tuple
│  ├─ source: str
│  └─ density_map: torch.Tensor [IF return_density_map=True]
│                                ↓ HEATMAP GENERATION
│
└─ HEATMAP GENERATION (if return_density_map=True)
   └─ generate_heatmap(density_map, original_image)
      ├─ Convert tensor to numpy
      ├─ Normalize to 0-255
      ├─ Resize to original image size
      ├─ Apply colormap (JET: red=high, blue=low)
      ├─ Blend with original image (60% heatmap, 40% original)
      └─ Return BGR numpy array (ready for cv2.imencode)
```

### YOLO Inference Pipeline

```
ml/src/models/yolo/api.py:predict()
│
├─ INPUT:
│  ├─ image: PIL.Image
│  ├─ checkpoint_path: "yolov8n.pt" (default)
│  ├─ source: "image|webcam|surveillance" (ignored, always 640x640)
│  ├─ return_boxes: boolean
│  └─ visualize: boolean
│
├─ GET MODEL
│  └─ model = get_model(checkpoint_path)
│  └─ YOLOv8Counter instance with device detection
│
├─ INFERENCE
│  └─ result = model.predict(img_np, return_boxes=True)
│     └─ OUTPUT: {count, boxes: [{bbox: [x1,y1,x2,y2], confidence: float}, ...]}
│
├─ TRANSFORM BOXES
│  └─ Convert from {bbox: [...], confidence: ...}
│  └─ To: {x1, y1, x2, y2, confidence}
│
├─ OUTPUT:
│  ├─ count: float
│  ├─ rounded_count: int
│  ├─ boxes: [{x1, y1, x2, y2, confidence}, ...]
│  ├─ inference_time_ms: float
│  ├─ device: str
│  └─ annotated_image: numpy BGR array [IF visualize=True]
│                                       ↓ (Ready to send as heatmap)
│
└─ HEATMAP GENERATION (if visualize=True)
   └─ generate_heatmap(boxes, original_image)
      ├─ Create density map from boxes (Gaussian blobs)
      ├─ Normalize density map
      ├─ Apply colormap (JET)
      ├─ Blend with original image
      └─ Return BGR numpy array
```

### TMTB (VMamba) Inference Pipeline

```
ml/src/models/tmtb/api.py:predict()
│
├─ INPUT:
│  ├─ image: PIL.Image
│  ├─ checkpoint_path: optional
│  ├─ source: "image|webcam|surveillance"
│  └─ return_density_map: boolean
│
├─ LOAD CONFIG
│  └─ Similar to CSRNet
│  └─ Get dimensions based on source
│
├─ RESIZE & PREPROCESS
│  └─ Similar to CSRNet
│
├─ INFERENCE
│  └─ density_map = model(img_tensor)
│  └─ count = density_map.sum().item()
│
├─ OUTPUT:
│  ├─ count: float
│  ├─ rounded_count: int
│  ├─ inference_time_ms: float
│  ├─ device: str
│  ├─ original_size: tuple
│  ├─ processed_size: tuple
│  └─ density_map: torch.Tensor [IF return_density_map=True]
│
└─ HEATMAP GENERATION (identical to CSRNet)
   └─ generate_heatmap(density_map, original_image)
```

---

## 📊 DATA PATH FLOWS (Broken & Working)

### 🟢 WORKING PATH: CSRNet with Heatmap

```
FRONTEND                           BACKEND                           ML
─────────────────────────────────────────────────────────────────────────

1. User clicks "Start"
   └─ WebSocket connects
   └─ Frame capture loop begins (100ms interval)

2. Each frame (100ms):
   Canvas.toDataURL()
   └─ data:image/jpeg;base64,/9j/4AAQ...

   Send JSON:
   {
     frame: "data:image/jpeg;base64,...",
     model: "csrnet",
     heatmap: true         ← USER ENABLED HEATMAP
   }

3. Backend receives
   │
   ├─ frame_data = extract base64
   ├─ model_type = "csrnet"
   ├─ return_heatmap = true    ← EXTRACTED CORRECTLY
   └─ image = decode to PIL

4. Model routing
   │
   └─ result = csrnet_api.predict(
        image,
        source="webcam",
        return_density_map=true  ← PASSED CORRECTLY
      )

5. CSRNet runs
   │
   ├─ Preprocess image
   ├─ Inference on GPU/CPU
   ├─ Generate density map tensor
   ├─ Calculate count = density_map.sum()
   └─ Return result with density_map ✅

6. Backend heatmap generation
   │
   ├─ Check condition:
   │  ├─ return_heatmap = true ✅
   │  ├─ "density_map" in result = true ✅
   │  └─ model_type != YOLO ✅
   │
   ├─ Generate heatmap_overlay
   │  ├─ Convert tensor to numpy
   │  ├─ Normalize to 0-255
   │  ├─ Resize to 640x480
   │  ├─ Apply colormap JET
   │  ├─ Blend with original (60/40)
   │  └─ Return BGR array ✅
   │
   ├─ cv2.imencode('.jpg', heatmap_overlay)
   │  └─ Returns buffer
   │
   ├─ base64.b64encode(buffer)
   │  └─ String
   │
   └─ response["heatmap"] = f"data:image/jpeg;base64,{...}" ✅

7. Send response JSON
   {
     "success": true,
     "count": 45,
     "fps": 8.3,
     "heatmap": "data:image/jpeg;base64,/9j/4AAQ..."  ✅
   }

8. Frontend receives
   │
   ├─ Parse JSON
   ├─ data.success = true ✅
   ├─ setCount(45)
   ├─ setFps(8.3)
   │
   └─ if data.heatmap:
      └─ setHeatmapImage(data.heatmap)  ✅
      └─ Component re-renders with heatmap image

9. Display
   └─ <img src={heatmapImage} />  ✅
   └─ Heatmap appears on screen ✅
```

### 🔴 BROKEN PATH: CSRNet without Heatmap

```
SCENARIO: Heatmap toggle OFF, but backend still tries to generate

FRONTEND                           BACKEND
─────────────────────────────────────────────

1. User clicks "Start"
   └─ enableHeatmap = false (initial state)

2. Each frame:
   {
     frame: "...",
     model: "csrnet",
     heatmap: false        ← DISABLED BY USER
   }

3. Backend receives
   ├─ return_heatmap = false
   └─ result = csrnet_api.predict(..., return_density_map=false)
      └─ CSRNet does NOT generate density_map tensor ❌

4. Heatmap generation check:
   │
   └─ if return_heatmap and "density_map" in result:
      ├─ return_heatmap = false ❌
      └─ Condition fails → NO heatmap generated

5. Response:
   {
     "success": true,
     "count": 45,
     "heatmap": undefined  ← FIELD MISSING
   }

6. Frontend receives
   │
   └─ if data.heatmap:
      └─ False → heatmapImage stays null

7. Display
   └─ <img src={null} />
   └─ No heatmap displayed ✅ (expected behavior)
```

### 🟡 PARTIALLY BROKEN PATH: Heatmap toggle ON but backend issue

```
SCENARIO: User enables heatmap but backend return_density_map not being passed

ISSUE: Backend receives heatmap=true but result doesn't have density_map

REASONS:
1. Model override: Model router called directly without return_density_map param
2. Legacy endpoint: REST API doesn't pass return_density_map
3. Model API bug: CSRNet ignore return_density_map parameter

RESULT:
response["heatmap"] field never populated
Frontend console: "⚠️ No heatmap in backend response"
Display: Blank heatmap area
```

### 🟢 WORKING PATH: YOLO with Heatmap

```
FRONTEND                           BACKEND                           ML
─────────────────────────────────────────────────────────────────────

1. User selects "yolo-nano"
   └─ selectedModel = "yolo-nano"

2. Each frame:
   {
     frame: "...",
     model: "yolo-nano",
     heatmap: true
   }

3. Backend routing
   └─ model_type = "yolo-nano"
   └─ In yolo_model_map = true
   └─ Call: yolo_api.predict(image, visualize=true)

4. YOLO runs
   ├─ Load YOLOv8n model
   ├─ Inference → get boxes + confidences
   ├─ annotated_image = draw boxes on image ✅
   └─ Return result with annotated_image ✅

5. Backend heatmap section
   ├─ Check: return_heatmap=true ✅
   ├─ Check: "annotated_image" in result ✅
   ├─ cv2.imencode annotated_image
   └─ response["heatmap"] = base64 ✅

6. Response:
   {
     "count": 3,
     "boxes": [...],
     "heatmap": "data:image/jpeg;base64,..."  ✅
   }

7. Frontend receives & displays ✅
```

---

## 🛑 STOP/CLEANUP SEQUENCE

### Frontend Cleanup (WebcamContext.stopEverything())

```
stopEverything() CALLED
│
├─ Step 1: Stop frame capture interval
│  └─ if intervalRef.current:
│     └─ clearInterval(intervalRef.current)
│     └─ intervalRef.current = null
│
├─ Step 2: Close WebSocket
│  └─ if wsRef.current?.readyState === WebSocket.OPEN:
│     └─ wsRef.current.close()
│     └─ wsRef.current = null
│     └─ Backend receives WebSocketDisconnect exception
│
├─ Step 3: Stop media stream
│  └─ if streamRef.current:
│     └─ getTracks().forEach(track => track.stop())
│     └─ Webcam stops
│     └─ streamRef.current = null
│
├─ Step 4: Clear video element
│  └─ if videoRef.current:
│     └─ videoRef.current.srcObject = null
│
└─ Result:
   ├─ isStreaming = false
   ├─ count = 0
   ├─ fps = 0
   ├─ status = "Ready"
   └─ All refs cleared
```

### Backend Cleanup (WebSocketDisconnect)

```
WebSocket Disconnect Event
│
└─ except WebSocketDisconnect:
   ├─ logger.info("❌ WebSocket disconnected")
   ├─ No graceful shutdown needed (connection already closed)
   ├─ Models stay in memory (cached)
   └─ Ready for next connection
```

### Full Application Cleanup (Component Unmount)

```
Webcam.js Component UNMOUNT
│
└─ useEffect(() => {
     return () => {
       console.log("🧹 Webcam component unmounting - cleaning up")
       stopEverything()
     }
   }, [])  ← Empty deps = only on unmount
   │
   └─ All resources released
   └─ No memory leaks
   └─ Webcam/canvas/websocket closed
```

---

## 🔗 CONTROL FLOW SUMMARY TABLE

| Flow                 | Entry        | Handler                      | Model            | Response               | Status         |
| -------------------- | ------------ | ---------------------------- | ---------------- | ---------------------- | -------------- |
| **Webcam**           | Start Button | `/ws/count`                  | CSRNet/TMTB/YOLO | JSON + heatmap         | ✅ Working     |
| **External Camera**  | Camera URL   | `/ws/external-camera`        | Any model        | JSON + frame + heatmap | ✅ Working     |
| **Image Upload**     | File Select  | `POST /api/v1/{model}/count` | CSRNet/TMTB/YOLO | JSON                   | ✅ Working     |
| **Heatmap (Webcam)** | Toggle ON    | `/ws/count`                  | CSRNet/TMTB      | base64 image           | ⚠️ Conditional |
| **Heatmap (YOLO)**   | Toggle ON    | `/ws/count`                  | YOLO             | base64 image           | ✅ Working     |
| **Tracking**         | Toggle ON    | `/ws/count`                  | YOLO             | tracks + unique_count  | ✅ Working     |
| **Cleanup**          | Stop Button  | stopEverything()             | -                | -                      | ✅ Working     |

---

**Report Generated:** November 25, 2025  
**Version:** Complete Control Flow Documentation
