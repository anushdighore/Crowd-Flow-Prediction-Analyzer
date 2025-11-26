# 📊 BACKEND DATA FLOW PATHS - Report 4

**Comprehensive Analysis of Request-Response Flows Through Backend Architecture**

---

## 📋 Executive Summary

The backend consists of **3 main data flow pathways**:

1. **REST API Flow** - Synchronous HTTP file uploads
2. **Webcam WebSocket Flow** - Real-time streaming for local webcam
3. **External Camera WebSocket Flow** - Streaming from IP cameras with full ML processing

Each pathway has distinct entry points, model routing logic, and response formats.

---

## 🗂️ FILE STRUCTURE & KEY COMPONENTS

```
backend/
├── app/
│   ├── main.py                          [MAIN ENTRY POINT]
│   │   ├── @app.websocket("/ws/count")
│   │   ├── @app.websocket("/ws/external-camera")
│   │   └── @app.websocket("/ws/video-process")
│   │
│   ├── api/v1/endpoints/
│   │   ├── csrnet.py                   [CSRNet REST API]
│   │   ├── tmtb.py                     [TMTB REST API]
│   │   ├── yolo.py                     [YOLO REST API]
│   │   └── pedestrian_tracking.py      [Tracking REST API]
│   │
│   ├── services/
│   │   ├── gated_model_router.py       [MODEL SELECTION LOGIC]
│   │   ├── ml_processor.py             [ML PROCESSING]
│   │   ├── stream_manager.py           [STREAM MANAGEMENT]
│   │   └── hls_packager.py             [HLS PACKAGING]
│   │
│   └── camera/
│       ├── camera_client.py            [EXTERNAL CAMERA CLIENT]
│       └── hls.py                      [HLS STREAMING]
│
└── ml/src/models/
    ├── csrnet/api.py                   [CSRNet INFERENCE]
    ├── tmtb/api.py                     [TMTB INFERENCE]
    ├── yolo/api.py                     [YOLO INFERENCE]
    └── unified_counter.py              [TRACKING ENGINE]
```

---

## 🌐 DATA FLOW PATH 1: REST API UPLOAD FLOW

### Entry Point: HTTP File Upload

```
POST /api/v1/{model}/count
Content-Type: multipart/form-data
Body: {file: binary_image}
```

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND: File Upload Form                                  │
│ ├─ User selects image file                                 │
│ ├─ Form.submit() → POST /api/v1/{model}/count             │
│ └─ multipart/form-data with File object                   │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND: FastAPI Endpoint Router (main.py:82)              │
│ ├─ app.include_router(csrnet_router, prefix="/api/v1")    │
│ ├─ app.include_router(tmtb_router, prefix="/api/v1")      │
│ ├─ app.include_router(yolo_router, prefix="/api/v1")      │
│ └─ Routes to appropriate endpoint file                     │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ ENDPOINT: csrnet.py (lines 25-58)                          │
│ @router.post("/count")                                     │
│ ├─ file: UploadFile = File(...)                           │
│ ├─ await file.read() → bytes                              │
│ ├─ Image.open(io.BytesIO(contents)) → PIL Image           │
│ └─ return_heatmap = False [DEFAULT]                       │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ ML INFERENCE: csrnet_api.predict()                         │
│ (ml/src/models/csrnet/api.py:91)                          │
│ ├─ image: PIL Image                                       │
│ ├─ source: "image"                                        │
│ ├─ return_density_map: False                              │
│ └─ [CSV PREPROCESSING, GPU INFERENCE, DENSITY MAPPING]    │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ ML RESPONSE: Result Dictionary                             │
│ {                                                          │
│   "count": 45,                                            │
│   "rounded_count": 45,                                    │
│   "raw_count": 45.2,                                      │
│   "inference_time_ms": 120.5,                             │
│   "device": "cuda",                                       │
│   "original_size": [640, 480],                            │
│   "processed_size": [320, 240]                            │
│ }                                                          │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ RESPONSE BUILDER (csrnet.py:35-53)                        │
│ ├─ response_data = {                                      │
│ │   "status": "success",                                 │
│ │   "count": 45,                                         │
│ │   "raw_count": 45.2,                                   │
│ │   "inference_time_ms": 120.5,                          │
│ │   "device": "cuda",                                    │
│ │   "original_size": [640, 480],                         │
│ │   "processed_size": [320, 240],                        │
│ │   "heatmap": None [IF return_heatmap=False]           │
│ │ }                                                       │
│ └─ return response_data as JSON                          │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND: HTTP Response                                    │
│ Response Code: 200 OK                                     │
│ Content-Type: application/json                            │
│ Body: {status, count, raw_count, inference_time, device}  │
│ ├─ Display count in UI                                   │
│ ├─ Show inference time                                   │
│ └─ Update statistics panel                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Parameters

| Component      | Parameter      | Default | Purpose                 |
| -------------- | -------------- | ------- | ----------------------- |
| **Upload**     | file           | -       | Binary image data       |
| **Routing**    | model          | csrnet  | Select model endpoint   |
| **Processing** | return_heatmap | false   | Heatmap generation flag |
| **Output**     | JSON           | -       | Count + metrics         |

### Response Schema

```json
{
  "status": "success",
  "count": 45,
  "raw_count": 45.2,
  "inference_time_ms": 120.5,
  "device": "cuda|cpu",
  "original_size": [width, height],
  "processed_size": [width, height],
  "heatmap": "data:image/jpeg;base64,..." [OPTIONAL]
}
```

---

## 🎥 DATA FLOW PATH 2: WEBCAM WEBSOCKET FLOW

### Entry Point: WebSocket Connection

```
WS ws://localhost:8000/ws/count
```

### Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│ FRONTEND: React WebcamContext.js                         │
│ ├─ Line 70-72: new WebSocket("ws://localhost:8000/...")  │
│ ├─ getUserMedia() → Video stream                         │
│ └─ Canvas capture every 100ms                           │
└────────┬─────────────────────────────────────────────────┘
         │ Periodic Send (100ms interval)
         ▼
┌──────────────────────────────────────────────────────────┐
│ FRAME ENCODING (Frontend)                                │
│ ├─ canvas.toDataURL("image/jpeg", 0.8)                  │
│ ├─ Base64 encode (~92KB per frame)                       │
│ └─ JSON payload:                                         │
│    {                                                      │
│      "frame": "data:image/jpeg;base64,...",             │
│      "model": "csrnet",                 [SELECTED]       │
│      "tracking": false,                 [OPTIONAL]       │
│      "heatmap": true,                   [OPTIONAL]       │
│      "threshold": 0.5                   [OPTIONAL]       │
│    }                                                      │
└────────┬─────────────────────────────────────────────────┘
         │ WebSocket.send()
         ▼
┌──────────────────────────────────────────────────────────┐
│ BACKEND: WebSocket Handler (main.py:168-350)            │
│ @app.websocket("/ws/count")                              │
│ ├─ await websocket.accept()                             │
│ └─ while True: await websocket.receive_json()           │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ DATA EXTRACTION (main.py:180-192)                        │
│ ├─ frame_data = data.get("frame") or data.get("image")  │
│ ├─ model_type = data.get("model", "csrnet")             │
│ ├─ enable_tracking = data.get("tracking", False)        │
│ ├─ return_heatmap = data.get("heatmap", False)          │
│ └─ [BASE64 DECODE] → PIL Image                          │
│    - if frame_data.startswith("data:image"):            │
│    - frame_data = frame_data.split(",")[1]              │
│    - image_bytes = base64.b64decode(frame_data)         │
│    - image = Image.open(io.BytesIO(image_bytes))        │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ MODEL SELECTION LOGIC (main.py:200-270)                  │
│ ├─ yolo_model_map = {                                   │
│ │   "yolo": "yolov8n.pt",                              │
│ │   "yolo-nano": "yolov8n.pt",                         │
│ │   "yolo-small": "yolov8s.pt",                        │
│ │   "yolo-medium": "yolov8m.pt",                       │
│ │   "yolo-large": "yolov8l.pt",                        │
│ │   "yolo-xlarge": "yolov8x.pt"                        │
│ │ }                                                      │
│ │                                                        │
│ └─ THREE POSSIBLE PATHS:                               │
└────────┬─────────────────────────────────────────────────┘
         │
    ┌────┼────┬────────────────────────────┐
    │    │    │                            │
    ▼    ▼    ▼                            ▼
  YOLO  TMTB CSRNet                  [HEATMAP LOGIC]
  Path  Path Path                    [path 306-317]
  ─────────────────────────────────────────────

[PATH A] YOLO (Object Detection with Tracking)
┌──────────────────────────────────────────────────────────┐
│ CONDITION: model_type in yolo_model_map                  │
│                                                          │
│ ├─ IF enable_tracking AND UnifiedCounter available:     │
│ │  └─ counter = get_tracking_counter(checkpoint)        │
│ │     ├─ img_array = np.array(image)                   │
│ │     ├─ if RGB: cv2.cvtColor() → BGR                  │
│ │     └─ result = counter.predict(                      │
│ │        img_array,                                     │
│ │        return_details=True,                           │
│ │        return_visualization=return_heatmap            │
│ │     )                                                  │
│ │     └─ model_name = "YOLO-{size}-Tracking"           │
│ │                                                       │
│ └─ ELSE: Use regular YOLO (no tracking)                │
│    └─ result = yolo_api.predict(                        │
│       image,                                            │
│       checkpoint_path=checkpoint,                       │
│       source="webcam",                                  │
│       return_boxes=True,                                │
│       visualize=return_heatmap                          │
│    )                                                     │
│       └─ model_name = "YOLO-{size}"                    │
│                                                         │
│ RESULT STRUCTURE:                                       │
│ {                                                       │
│   "count": 5,                                          │
│   "boxes": [{x1, y1, x2, y2, confidence}, ...],       │
│   "inference_time_ms": 8.5,                           │
│   "annotated_image": numpy_array [IF visualize=true]  │
│ }                                                       │
└──────────────────────────────────────────────────────────┘

[PATH B] TMTB (Density Estimation - VMamba)
┌──────────────────────────────────────────────────────────┐
│ CONDITION: model_type == "tmtb"                          │
│                                                          │
│ ├─ result = tmtb_api.predict(                           │
│ │   image,                                              │
│ │   source="webcam"                                    │
│ │ )                                                     │
│ │                                                       │
│ └─ model_name = "TMTB"                                 │
│                                                         │
│ RESULT STRUCTURE:                                       │
│ {                                                       │
│   "count": 45,                                         │
│   "rounded_count": 45,                                │
│   "inference_time_ms": 120.5,                         │
│   "device": "cuda|cpu"                                │
│   "density_map": numpy_array [IF requested]           │
│ }                                                       │
└──────────────────────────────────────────────────────────┘

[PATH C] CSRNet (Density Estimation - DEFAULT)
┌──────────────────────────────────────────────────────────┐
│ CONDITION: else (default)                                │
│                                                          │
│ ├─ result = csrnet_api.predict(                         │
│ │   image,                                              │
│ │   source="webcam",                                   │
│ │   return_density_map=return_heatmap  [KEY PARAM]     │
│ │ )                                                     │
│ │                                                       │
│ ├─ model_name = "CSRNet"                               │
│ │                                                       │
│ └─ LOGGING (Line 275-276):                             │
│    └─ logger.info(f"🔍 CSRNet result keys: ...")       │
│    └─ logger.info(f"🔍 return_heatmap={...}")          │
│                                                         │
│ RESULT STRUCTURE:                                       │
│ {                                                       │
│   "count": 45,                                         │
│   "rounded_count": 45,                                │
│   "inference_time_ms": 120.5,                         │
│   "device": "cuda|cpu",                              │
│   "density_map": numpy_array [IF return_density_map]  │
│ }                                                       │
└──────────────────────────────────────────────────────────┘

[HEATMAP GENERATION LOGIC] (main.py:306-317)
┌──────────────────────────────────────────────────────────┐
│ CONDITION: return_heatmap AND "density_map" in result    │
│            AND model_type NOT in yolo_model_map          │
│                                                          │
│ IF TRUE:                                                 │
│  ├─ logger.info(f"🔥 Generating heatmap...")            │
│  ├─ heatmap_overlay = csrnet_api.generate_heatmap(     │
│  │   result["density_map"],                            │
│  │   image                                             │
│  │ )                                                    │
│  ├─ _, buffer = cv2.imencode('.jpg', heatmap_overlay) │
│  ├─ img_base64 = base64.b64encode(buffer).decode()    │
│  ├─ response["heatmap"] = f"data:image/jpeg;..."      │
│  └─ logger.info(f"✅ Heatmap generated...")            │
│                                                         │
│ ELSE:                                                   │
│  └─ logger.info(f"⚠️ Heatmap NOT generated - ...")     │
│     └─ Reasons: return_heatmap=False OR              │
│        density_map missing OR YOLO model              │
│                                                         │
│ FOR YOLO (different heatmap logic):                     │
│  ├─ IF return_heatmap AND "annotated_image" in result: │
│  │  └─ Use result["annotated_image"] as heatmap      │
│  └─ response["heatmap"] = base64_encoded_image        │
└──────────────────────────────────────────────────────────┘
```

### Frame Counter & Response Building (main.py:278-350)

```python
frame_number += 1  # Increment after model selection

response = {
    "success": True,
    "model": model_name.lower(),                    # "csrnet|tmtb|yolo-nano|..."
    "count": result.get("count", 0),                # Crowd count
    "inference_time_ms": result.get("inference_time_ms", 0),  # Latency
    "frame_number": frame_number,                   # Frame index
    "fps": 1000 / inference_time if inference_time > 0 else 0
}

# Model-specific additions:
if model_type.lower() in yolo_model_map:
    response["boxes"] = result.get("boxes", [])
    response["num_detections"] = len(result.get("boxes", []))

    if result.get("boxes"):
        confidences = [box.get("confidence", 0) for box in result.get("boxes", [])]
        if confidences:
            response["average_confidence"] = sum(confidences) / len(confidences)

    # Heatmap for YOLO
    if return_heatmap and "annotated_image" in result:
        response["heatmap"] = base64_encoded_image

# Tracking data
if enable_tracking and model_type.lower() in yolo_model_map:
    response["unique_count"] = result.get("unique_count", response["count"])
    response["tracks"] = result.get("tracks", [])
    if "speed_stats" in result:
        response["speed_stats"] = result["speed_stats"]

    # Advanced metrics
    try:
        counter = get_tracking_counter(checkpoint)
        if counter is not None:
            advanced_metrics = counter.get_advanced_metrics(
                frame_shape=frame_shape,
                frame_rate=30,
                frame_step=25
            )
            response["advanced_metrics"] = advanced_metrics
    except Exception as e:
        logger.warning(f"Advanced metrics error: {e}")

await websocket.send_json(response)  # Send back to frontend
```

### Response Schema

```json
{
  "success": true,
  "model": "csrnet|tmtb|yolo-nano|yolo-small|...",
  "count": 45,
  "inference_time_ms": 120.5,
  "frame_number": 125,
  "fps": 8.3,
  "boxes": [],  [IF YOLO]
  "num_detections": 0,  [IF YOLO]
  "average_confidence": 0.92,  [IF YOLO WITH DETECTIONS]
  "heatmap": "data:image/jpeg;base64,...",  [IF REQUESTED]
  "unique_count": 45,  [IF TRACKING ENABLED]
  "tracks": [],  [IF TRACKING ENABLED]
  "speed_stats": {},  [IF TRACKING ENABLED]
  "advanced_metrics": {}  [IF TRACKING ENABLED]
}
```

---

## 📹 DATA FLOW PATH 3: EXTERNAL CAMERA WEBSOCKET FLOW

### Entry Point: WebSocket Connection with Camera URL

```
WS ws://localhost:8000/ws/external-camera
```

### Configuration Phase

```
Client sends:
{
  "camera_url": "rtsp://192.168.1.100:554/stream",
  "model": "csrnet",
  "tracking": false
}

Server responds:
{
  "success": true,
  "message": "Camera URL configured",
  "camera_url": "rtsp://192.168.1.100:554/stream"
}
```

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND: ExternalCam.js                                    │
│ ├─ onCameraUrlChange(url)                                  │
│ ├─ connectWebSocket()                                      │
│ └─ Send configuration message                              │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND: WebSocket Handler (main.py:374-600)               │
│ @app.websocket("/ws/external-camera")                       │
│                                                             │
│ INITIALIZATION:                                             │
│ ├─ await websocket.accept()                                │
│ ├─ frame_number = 0                                        │
│ ├─ camera_url = None                                       │
│ ├─ model_type = "csrnet" [DEFAULT]                         │
│ └─ enable_tracking = False                                 │
│                                                             │
│ CONFIG MESSAGE RECEPTION:                                   │
│ ├─ if "camera_url" in data:                               │
│ │  ├─ camera_url = data["camera_url"]                    │
│ │  ├─ model_type = data.get("model", "csrnet")           │
│ │  ├─ enable_tracking = data.get("tracking", False)      │
│ │  ├─ logger.info(f"📹 External camera URL set: ...")    │
│ │  └─ Send config response                                │
│ │     {"success": true, "message": "...", "camera_url"} │
│ │                                                         │
│ └─ continue [WAIT FOR NEXT MESSAGE]                       │
│                                                             │
│ FRAME REQUEST:                                              │
│ ├─ if data.get("action") == "get_frame":                  │
│ └─ [PROCEED TO FRAME PROCESSING]                          │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ CAMERA FRAME RETRIEVAL (main.py:410-420)                   │
│                                                             │
│ ├─ frame = await camera_client.get_frame(camera_url)      │
│ │  └─ [CAN RETURN None IF FAILED]                         │
│ │                                                         │
│ ├─ if frame is None:                                      │
│ │  └─ Send error response                                │
│ │     {"success": false, "error": "Failed to get frame"} │
│ │     continue                                            │
│ │                                                         │
│ └─ CONVERSION:                                             │
│    ├─ frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) │
│    └─ pil_image = Image.fromarray(frame_rgb)             │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ MODEL SELECTION & ROUTING (main.py:432-505)                │
│                                                             │
│ yolo_model_map = {                                         │
│   "yolo": "yolov8n.pt",                                   │
│   "yolo-nano": "yolov8n.pt",                              │
│   "yolo-small": "yolov8s.pt",                             │
│   "yolo-medium": "yolov8m.pt",                            │
│   "yolo-large": "yolov8l.pt",                             │
│   "yolo-xlarge": "yolov8x.pt"                             │
│ }                                                          │
│                                                             │
│ THREE POSSIBLE PATHS:                                       │
└────────┬────────────────────────────────────────────────────┘
         │
    ┌────┼────┬────────────────────────────────────┐
    │    │    │                                    │
    ▼    ▼    ▼                                    ▼
  YOLO  Legacy  Model-Router              [HEATMAP]
  Track Models   (Recommended)             [Logic]
  Path  Path     Path
  ────────────────────────────────────────────────

[PATH A] YOLO WITH TRACKING (IF enabled AND model is YOLO)
┌─────────────────────────────────────────────────────────────┐
│ CONDITION: enable_tracking AND model_type in yolo_model_map│
│            AND UnifiedCounter is not None                   │
│                                                             │
│ ├─ checkpoint = yolo_model_map[model_type]                │
│ ├─ counter = get_tracking_counter(checkpoint)              │
│ │                                                           │
│ ├─ img_array = np.array(pil_image)  [PIL to numpy]        │
│ ├─ if RGB: img_array = cv2.cvtColor(img_array, COLOR_RGB2BGR)
│ │                                                           │
│ ├─ result = counter.predict(                               │
│ │   img_array,                                             │
│ │   return_details=True,                                  │
│ │   return_visualization=True  [ALWAYS TRUE FOR EXTERNAL] │
│ │ )                                                         │
│ │                                                           │
│ ├─ model_name = f"YOLO-{size}-Tracking"                   │
│ │                                                           │
│ └─ if 'annotated_image' in result:                         │
│    └─ heatmap_frame = result['annotated_image']           │
│    └─ else: heatmap_frame = None                          │
│                                                             │
│ EXCEPTION HANDLING:                                         │
│ └─ except Exception as track_err:                          │
│    ├─ logger.error(f"Tracking error: {track_err}")        │
│    ├─ enable_tracking = False                             │
│    └─ Fall through to model router                        │
└─────────────────────────────────────────────────────────────┘

[PATH B] MODEL ROUTER (Recommended approach)
┌─────────────────────────────────────────────────────────────┐
│ CONDITION: NOT enable_tracking OR not YOLO                 │
│            AND model_router is available                    │
│                                                             │
│ ├─ logger.info(f"🔀 Routing external camera to ...")      │
│ │                                                           │
│ ├─ result = model_router.predict(                          │
│ │   pil_image,                                            │
│ │   model_type=model_type,                               │
│ │   source="surveillance",                               │
│ │   return_density_map=True,                             │
│ │   return_boxes=(model_type in yolo_model_map)          │
│ │ )                                                        │
│ │                                                           │
│ ├─ model_name = result.get('model_name', model_type.upper())
│ │                                                           │
│ └─ HEATMAP GENERATION (Via model_router):                  │
│    ├─ heatmap_frame = None  [INITIALIZE]                  │
│    │                                                        │
│    ├─ try:                                                  │
│    │  └─ if model_type in yolo_model_map:                │
│    │     ├─ if result.get('boxes') and len(boxes) > 0: │
│    │     │  └─ heatmap_frame = model_router.generate_heatmap(
│    │     │     model_type, result, pil_image          │
│    │     │    )                                           │
│    │     │     └─ logger.info(f"📦 Generating heatmap...")
│    │     │                                                │
│    │     └─ else:                                         │
│    │        └─ logger.warning("⚠️ No boxes detected")    │
│    │                                                       │
│    │  └─ else [CSRNet/TMTB]:                            │
│    │     └─ heatmap_frame = model_router.generate_heatmap(
│    │        model_type, result, pil_image              │
│    │       )                                              │
│    │                                                       │
│    └─ except Exception as heatmap_error:                   │
│       ├─ logger.error(f"Heatmap error: ...")            │
│       └─ heatmap_frame = None                            │
└─────────────────────────────────────────────────────────────┘

[PATH C] LEGACY FALLBACK (if model_router unavailable)
┌─────────────────────────────────────────────────────────────┐
│ CONDITION: NOT enable_tracking AND NOT model_router        │
│                                                             │
│ ├─ if model_type == "tmtb" and tmtb_api:                  │
│ │  └─ result = tmtb_api.predict(                          │
│ │     pil_image,                                          │
│ │     source="surveillance",                             │
│ │     return_density_map=True                            │
│ │    )                                                     │
│ │     model_name = "TMTB"                                │
│ │     heatmap_frame = None                               │
│ │                                                         │
│ └─ else [DEFAULT CSRNet]:                                │
│    └─ result = csrnet_api.predict(                       │
│       pil_image,                                         │
│       source="surveillance",                            │
│       return_density_map=True                           │
│      )                                                    │
│      model_name = "CSRNet"                              │
│      heatmap_frame = None                               │
└─────────────────────────────────────────────────────────────┘
```

### Frame Encoding & Response Building (main.py:520-560)

```python
frame_number += 1

# Encode original frame as JPEG
_, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
frame_base64 = base64.b64encode(buffer).decode('utf-8')

# Encode heatmap frame if available
heatmap_base64 = None
if heatmap_frame is not None:
    _, heatmap_buffer = cv2.imencode('.jpg', heatmap_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    heatmap_base64 = base64.b64encode(heatmap_buffer).decode('utf-8')

response_data = {
    "success": True,
    "model": model_name.lower(),
    "count": result.get("rounded_count", result.get("count", 0)),
    "raw_count": result.get("count", 0),
    "inference_time_ms": result.get("inference_time_ms", 0),
    "device": result.get("device", "unknown"),
    "frame_number": frame_number,
    "fps": 1000 / inference_time if inference_time > 0 else 0,
    "frame": f"data:image/jpeg;base64,{frame_base64}"
}

# Add tracking data if enabled
if enable_tracking and model_type.lower() in yolo_model_map:
    response_data["unique_count"] = result.get("unique_count", response_data["count"])
    response_data["tracks"] = result.get("tracks", [])
    if "speed_stats" in result:
        response_data["speed_stats"] = result["speed_stats"]

    # Add advanced metrics
    try:
        counter = get_tracking_counter(checkpoint)
        if counter is not None:
            advanced_metrics = counter.get_advanced_metrics(
                frame_shape=(frame.shape[0], frame.shape[1]),
                frame_rate=30,
                frame_step=25
            )
            response_data["advanced_metrics"] = advanced_metrics
    except Exception as e:
        logger.warning(f"Advanced metrics error: {e}")

# Add heatmap if available
if heatmap_base64:
    response_data["heatmap"] = f"data:image/jpeg;base64,{heatmap_base64}"

await websocket.send_json(response_data)
```

### Response Schema

```json
{
  "success": true,
  "model": "csrnet|tmtb|yolo-nano|...",
  "count": 45,
  "raw_count": 45.0,
  "inference_time_ms": 120.5,
  "device": "cuda|cpu|unknown",
  "frame_number": 125,
  "fps": 8.3,
  "frame": "data:image/jpeg;base64,...",  [CURRENT FRAME]
  "heatmap": "data:image/jpeg;base64,...",  [IF AVAILABLE]
  "unique_count": 45,  [IF TRACKING]
  "tracks": [],  [IF TRACKING]
  "speed_stats": {},  [IF TRACKING]
  "advanced_metrics": {}  [IF TRACKING]
}
```

---

## 🔀 MODEL SELECTION DECISION TREE

```
┌─ User selects model from frontend UI
│
└─ Message sent to backend with model_type parameter
   │
   ├─ Check if model_type in yolo_model_map
   │  │
   │  ├─ YES [YOLO SELECTED]
   │  │  │
   │  │  ├─ Check if tracking enabled
   │  │  │  ├─ YES → Use UnifiedCounter (with Kalman tracking)
   │  │  │  │       └─ result = counter.predict(..., return_visualization=True)
   │  │  │  │
   │  │  │  └─ NO → Use YOLO API directly
   │  │  │          └─ result = yolo_api.predict(..., visualize=True)
   │  │  │
   │  │  └─ Response includes: boxes, confidence, annotated_image
   │  │
   │  └─ NO [DENSITY ESTIMATION SELECTED]
   │     │
   │     ├─ Check if model_type == "tmtb"
   │     │  │
   │     │  ├─ YES [TMTB/VMAMBA SELECTED]
   │     │  │  └─ result = tmtb_api.predict(image, source="webcam")
   │     │  │     └─ Returns: count, raw_count, inference_time_ms, device
   │     │  │
   │     │  └─ NO [DEFAULT TO CSRNET]
   │     │     └─ result = csrnet_api.predict(image, source="webcam", return_density_map=return_heatmap)
   │     │        └─ Returns: count, density_map (if requested), inference_time_ms, device
   │     │
   │     └─ Response includes: count, fps, optionally density_map
   │
   └─ Send response to frontend with model-specific data
```

---

## 📊 DATA SIZE & PERFORMANCE METRICS

### Typical Frame Sizes

| Component             | Size    | Notes                    |
| --------------------- | ------- | ------------------------ |
| **Webcam Frame**      | 640×480 | Canvas capture           |
| **JPEG Encoding**     | 92KB    | ~80% quality             |
| **Base64 Encoded**    | ~123KB  | Base64 adds 33% overhead |
| **WebSocket Message** | ~125KB  | JSON wrapper ~1KB        |
| **Heatmap Image**     | ~100KB  | Overlay visualization    |
| **Response Total**    | ~225KB  | With heatmap included    |

### Processing Times (Inference Only)

| Model          | CPU       | GPU (CUDA) | Source             |
| -------------- | --------- | ---------- | ------------------ |
| **CSRNet**     | 350-500ms | 120-150ms  | Density estimation |
| **TMTB**       | 400-600ms | 140-180ms  | VMamba model       |
| **YOLO-Nano**  | 40-60ms   | 8-12ms     | Object detection   |
| **YOLO-Small** | 60-100ms  | 12-18ms    | Object detection   |

### FPS Calculation

```
FPS = 1000 / inference_time_ms

Example:
- CSRNet GPU: 1000 / 120 = 8.3 FPS
- YOLO-Nano GPU: 1000 / 10 = 100 FPS
- Total latency includes: frame capture (10ms) + processing + encoding
```

---

## 🔗 DATA DEPENDENCIES & IMPORTS

### Model Loading (main.py:40-54)

```python
try:
    from models.csrnet import api as csrnet_api      # CSRNet inference
    from models.tmtb import api as tmtb_api          # TMTB/VMamba inference
    from models.yolo import api as yolo_api          # YOLO detection
    from models.unified_counter import UnifiedCounter # Tracking engine
    from app.services.gated_model_router import get_router  # Model selection

    model_router = get_router()  # Initialize router
    logger.info(f"✅ Available models: {model_router.get_available_models()}")

except ImportError as e:
    logger.warning(f"Could not import model APIs: {e}")
    csrnet_api = tmtb_api = yolo_api = None
    UnifiedCounter = None
    model_router = None
```

### Router Inclusion (main.py:82-87)

```python
app.include_router(csrnet_router, prefix="/api/v1", tags=["csrnet"])
app.include_router(tmtb_router, prefix="/api/v1", tags=["tmtb"])
app.include_router(yolo_router, prefix="/api/v1", tags=["yolo"])
app.include_router(pedestrian_tracking_router, prefix="/api/v1", tags=["pedestrian-tracking"])
app.include_router(camera_router, prefix="/api", tags=["camera"])
app.include_router(hls_router, prefix="/api", tags=["hls"])
```

---

## ⚠️ ERROR HANDLING PATHS

### Webcam Flow Error Cases

```
1. No frame data received
   └─ Response: {"success": false, "error": "No frame data received"}

2. Base64 decode fails
   └─ Exception caught, user notified via frontend

3. Model inference error
   └─ Fallback to default model (CSRNet)

4. Heatmap generation fails
   └─ Response sent without heatmap field
   └─ Error logged: "❌ Heatmap generation failed: {error}"

5. Tracking counter not available
   └─ Fallback to regular model (no tracking)
   └─ Model name adjusted accordingly

6. WebSocket disconnect
   └─ Connection closes
   └─ Cleanup performed automatically
```

### External Camera Error Cases

```
1. Camera URL not set
   └─ Response: {"success": false, "error": "Camera URL not set"}

2. Frame retrieval fails
   └─ Response: {"success": false, "error": "Failed to get frame from camera"}

3. Model router unavailable
   └─ Fallback to legacy mode (tmtb_api or csrnet_api)

4. Advanced metrics calculation fails
   └─ Response still sent, metrics field omitted
   └─ Warning logged, no fatal error

5. WebSocket disconnect
   └─ Connection closes
   └─ Cleanup performed automatically
```

---

## 📈 STATE TRANSITIONS

### WebSocket Connection States

```
┌──────────────┐
│   CREATED    │  new WebSocket("ws://...")
└──────┬───────┘
       │ await websocket.accept()
       ▼
┌──────────────┐
│  CONNECTED   │  Ready to receive/send messages
└──────┬───────┘
       │ while True: await websocket.receive_json()
       ├────┬────┬────────────────────┐
       │    │    │                    │
       ▼    ▼    ▼                    ▼
     CONFIG  FRAME  VIDEO         [ERROR]
     MSG    MSG    MSG            ↓
       │    │    │        [Close connection]
       │    │    │
       ├─── receive_json() ────────┤
       │                           │
       └─── send_json(response) ───┤
       │                           │
       └─── continue loop ─────────┘

[ON DISCONNECT]
   ↓
┌──────────────────────────┐
│ WebSocketDisconnect      │  Caught by exception handler
│ Exception caught         │  Cleanup resources
└──────────────────────────┘
```

---

## 🎯 KEY PARAMETERS SUMMARY

### Frontend → Backend Parameters

| Parameter    | Type            | Default  | Purpose             | Path      |
| ------------ | --------------- | -------- | ------------------- | --------- |
| `frame`      | string (base64) | -        | Image data          | All       |
| `model`      | string          | "csrnet" | Model selection     | WebSocket |
| `tracking`   | boolean         | false    | Enable tracking     | WebSocket |
| `heatmap`    | boolean         | false    | Heatmap generation  | WebSocket |
| `threshold`  | float           | 0.5      | Detection threshold | WebSocket |
| `camera_url` | string          | -        | IP camera address   | ExtCam    |

### Backend → Frontend Response Fields

| Field               | Type            | Condition    | Purpose            |
| ------------------- | --------------- | ------------ | ------------------ |
| `success`           | boolean         | Always       | Request success    |
| `model`             | string          | Always       | Model used         |
| `count`             | number          | Always       | Crowd count        |
| `inference_time_ms` | number          | Always       | Processing latency |
| `fps`               | number          | Always       | Frames per second  |
| `heatmap`           | string (base64) | If requested | Visualization      |
| `boxes`             | array           | If YOLO      | Detection boxes    |
| `tracks`            | array           | If tracking  | Track data         |
| `speed_stats`       | object          | If tracking  | Movement analytics |
| `advanced_metrics`  | object          | If tracking  | Crowd metrics      |

---

## 📌 CRITICAL INTEGRATION POINTS

### 1. **Heatmap Generation Condition** (main.py:306)

```python
if return_heatmap and "density_map" in result and model_type.lower() not in yolo_model_map:
    # Generate heatmap ONLY if ALL conditions met
```

**All three conditions must be TRUE:**

- `return_heatmap = True` (frontend sent heatmap=true)
- `"density_map" in result` (CSRNet/TMTB returned density map)
- `model_type not in yolo_model_map` (Not YOLO model)

### 2. **Model Routing Logic** (main.py:200-270)

```python
# Check YOLO first (specific)
if model_type.lower() in yolo_model_map:
    # YOLO path
# Check TMTB (specific)
elif model_type.lower() == "tmtb":
    # TMTB path
# Default to CSRNet
else:
    # CSRNet path
```

### 3. **Frame Encoding/Decoding** (main.py:188-194)

```python
# Frontend: canvas.toDataURL('image/jpeg', 0.8)
# Produces: "data:image/jpeg;base64,/9j/4AAQ..."
# Backend extraction:
frame_data = frame_data.split(",")[1]  # Remove prefix
image_bytes = base64.b64decode(frame_data)
image = Image.open(io.BytesIO(image_bytes))
```

### 4. **Model Import Path** (main.py:40-54)

```python
ml_path = Path(__file__).parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

from models.csrnet import api as csrnet_api
```

---

## 📊 COMPLETE DATA FLOW SUMMARY TABLE

| Flow                | Entry                      | Handler      | Processing                     | Response     | Use Case            |
| ------------------- | -------------------------- | ------------ | ------------------------------ | ------------ | ------------------- |
| **REST Upload**     | POST /api/v1/{model}/count | csrnet.py:25 | HTTP sync                      | JSON         | Single image upload |
| **Webcam**          | WS /ws/count               | main.py:168  | Real-time async                | JSON         | Live webcam stream  |
| **External Camera** | WS /ws/external-camera     | main.py:374  | Real-time async + frame encode | JSON + frame | IP camera streaming |

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] All model APIs imported successfully
- [ ] WebSocket endpoints accessible
- [ ] Model router initialized
- [ ] Camera client configured
- [ ] CORS middleware properly configured
- [ ] Frontend can reach backend at localhost:8000
- [ ] Base64 encoding/decoding working
- [ ] Heatmap generation functions available
- [ ] Tracking counter optional but working if available
- [ ] Error logging configured

---

**Report Generated:** November 25, 2025  
**Version:** Report 4 - Complete Backend Data Flow Paths  
**Status:** ✅ COMPREHENSIVE ANALYSIS COMPLETE
