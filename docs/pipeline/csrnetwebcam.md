# 🎬 CSRNet Webcam Pipeline - Complete Architecture

**Document Type:** Pipeline Control Flow & Data Flow  
**System:** Crowd Flow Prediction Analyzer  
**Pipeline:** Webcam → Canvas → WebSocket → Backend ML → Frontend Display  
**Model:** CSRNet (Crowd Scene Recognition Network)  
**Date:** November 25, 2025

---

## 📑 TABLE OF CONTENTS

1. [Pipeline Overview](#pipeline-overview)
2. [Component Architecture](#component-architecture)
3. [Control Flow Diagram](#control-flow-diagram)
4. [Data Flow Breakdown](#data-flow-breakdown)
5. [Module Components](#module-components)
6. [WebSocket Communication](#websocket-communication)
7. [Backend Processing](#backend-processing)
8. [Frontend State Management](#frontend-state-management)

---

## 🎯 PIPELINE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CSRNet Webcam Pipeline                             │
│                                                                           │
│  FRONTEND (React)          │         NETWORK (WebSocket)      │  BACKEND  │
│                            │                                  │  (FastAPI)│
│                            │                                  │           │
│  1. Webcam Capture    ──→  │                                  │           │
│  2. Canvas Drawing    ──→  │                                  │           │
│  3. JPEG Encoding     ──→  │                                  │           │
│  4. Base64 Encoding   ──→  │  5. WebSocket Send  ────────→   │ 6. Receive│
│  5. JSON Wrapper      ──→  │                                  │ 7. Decode │
│                            │                                  │ 8. CSRNet │
│                            │                                  │ 9. Generate
│                            │                       ←─────────   10.Response
│  11. Parse JSON       ←─────  12. WebSocket Recv              │           │
│  12. Update State     ←─────                                  │           │
│  13. Render Heatmap   ←─────                                  │           │
│                            │                                  │           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ COMPONENT ARCHITECTURE

### **TIER 1: FRONTEND COMPONENTS (React)**

#### **A. WebcamContext.js** → Context Provider

- **File Path:** `frontend/src/context/WebcamContext.js`
- **Purpose:** Global state management for webcam operations
- **State Variables:**

  - `isStreaming` (boolean) - Stream status
  - `selectedModel` (string) - Active model ("CSRNet")
  - `enableHeatmap` (boolean) - Heatmap visualization toggle
  - `count` (number) - Crowd count
  - `fps` (number) - Frames per second
  - `inferenceTime` (number) - Model inference time in ms
  - `heatmapImage` (string) - Base64 heatmap image
  - `densityStats` (object) - Density map statistics
  - `error` (string) - Error messages
  - `status` (string) - Current operation status
  - `results` (object) - Full backend response

- **Refs:**

  - `videoRef` - HTML5 video element
  - `canvasRef` - Canvas element for frame capture
  - `streamRef` - MediaStream object
  - `wsRef` - WebSocket connection
  - `intervalRef` - Frame capture interval

- **Key Functions:**

  ```
  ┌─ connectWebSocket()
  │  ├─ Returns Promise<WebSocket>
  │  ├─ Connects to: ws://localhost:8000/ws/count
  │  ├─ Sets up event handlers:
  │  │  ├─ onopen → Resolve WebSocket
  │  │  ├─ onmessage → Parse backend response
  │  │  ├─ onerror → Set error state
  │  │  └─ onclose → Cleanup resources
  │  └─ Returns WebSocket object
  │
  ├─ startWebcam()
  │  ├─ Returns Promise<boolean>
  │  ├─ Requests camera permissions (getUserMedia)
  │  ├─ Applies resolution constraints
  │  ├─ Sets videoRef.srcObject = stream
  │  ├─ Waits for video metadata
  │  └─ Returns true on success
  │
  ├─ captureAndSend()
  │  ├─ Captures frame from video element
  │  ├─ Draws to canvas (640x480 typical)
  │  ├─ Converts canvas → JPEG data URI
  │  ├─ Sends JSON via WebSocket
  │  └─ No return value
  │
  ├─ startStreaming()
  │  ├─ Calls startWebcam()
  │  ├─ Calls connectWebSocket()
  │  ├─ Starts frame capture interval (100ms)
  │  ├─ Calls captureAndSend() repeatedly
  │  └─ Sets isStreaming = true
  │
  └─ stopEverything()
     ├─ Clears interval (stops frame capture)
     ├─ Closes WebSocket
     ├─ Stops media stream tracks
     ├─ Nullifies refs
     └─ Sets isStreaming = false
  ```

---

#### **B. Webcam.js** → Page Component

- **File Path:** `frontend/src/pages/webcam/Webcam.js`
- **Purpose:** Main UI container for webcam operations
- **Dependencies:**
  - Imports `useWebcam()` hook from WebcamContext
  - Imports `useAuth()` hook for authentication
- **Render Elements:**

  - `<Nav>` - Navigation bar
  - `<Menu>` - Left sidebar menu
  - `<video ref={videoRef}>` - Video element
  - `<canvas ref={canvasRef}>` - Hidden canvas
  - Status panel display
  - Count display panel
  - FPS/inference time metrics
  - Error alert
  - Toast notifications

- **User Controls:**
  - Start/Stop streaming buttons
  - Model selection buttons (from RightMenu)
  - Heatmap toggle checkbox
  - Tracking enable checkbox
  - Resolution selector

---

#### **C. CameraStream.js** → Streaming Component

- **File Path:** `frontend/src/components/Camera/CameraStream.js`
- **Purpose:** Low-level webcam stream management
- **Props:**
  - `deviceId` (string) - Camera device identifier
  - `onFrameCapture` (function) - Callback on frame capture
- **Methods:**
  - `captureFrame()` - Extracts frame from video element

---

#### **D. HeatmapCard.js** → Display Component

- **File Path:** `frontend/src/components/Models/CSRNet/HeatmapCard.js`
- **Purpose:** Displays heatmap image overlay
- **Renders:**
  - `<img src={heatmapImage} />` - Base64 image display
  - Status messages if heatmap missing

---

#### **E. CSRNetCard.js** → Results Component

- **File Path:** `frontend/src/components/Models/CSRNet/CSRNetCard.js`
- **Purpose:** Displays full JSON response from backend
- **Renders:**
  - Count value
  - Inference time
  - Raw density stats
  - Pretty-printed JSON response

---

### **TIER 2: NETWORK LAYER**

#### **WebSocket Protocol**

- **URL:** `ws://localhost:8000/ws/count`
- **Protocol:** JSON over WebSocket (binary frames)
- **Handshake:** HTTP upgrade request
- **Message Rate:** Every 100ms (10 FPS typical)

---

### **TIER 3: BACKEND COMPONENTS (FastAPI)**

#### **A. main.py** → Application Core

- **File Path:** `backend/app/main.py`
- **Purpose:** FastAPI application instance and WebSocket handlers
- **WebSocket Endpoint:**

  ```
  @app.websocket("/ws/count")
  async def websocket_count(websocket: WebSocket)
  ```

- **Key Variables:**

  - `frame_number` (int) - Frame counter
  - `model_type` (string) - Selected model
  - `enable_tracking` (boolean) - Tracking flag
  - `return_heatmap` (boolean) - Heatmap generation flag

- **Execution Flow:**
  ```
  1. Accept WebSocket connection
  2. Loop: await websocket.receive_json()
  3. Extract frame data (base64 string)
  4. Model selection:
     ├─ If YOLO model requested
     │  ├─ Check tracking flag
     │  ├─ Use UnifiedCounter (if enabled)
     │  └─ Otherwise use yolo_api
     ├─ If TMTB model requested
     │  └─ Use tmtb_api
     └─ Default: Use csrnet_api
  5. Call predict() with frame
  6. If heatmap enabled:
     ├─ Extract density_map from result
     └─ Call generate_heatmap()
  7. Build response JSON
  8. Send via websocket.send_json()
  9. Repeat
  ```

---

#### **B. api.py** → CSRNet Model API

- **File Path:** `backend/ml/src/models/csrnet/api.py`
- **Purpose:** Unified CSRNet prediction interface
- **Functions:**

  ```
  ┌─ get_model(checkpoint_path: str) → torch.nn.Module
  │  ├─ Checks _model_cache
  │  ├─ If not cached: calls load_csrnet()
  │  ├─ Caches model
  │  └─ Returns CSRNet model instance
  │
  ├─ get_preprocessor() → torchvision.transforms
  │  ├─ Returns _preprocessor singleton
  │  ├─ Initializes if needed
  │  └─ Contains normalization transforms
  │
  ├─ generate_heatmap(
  │  │  density_map: torch.Tensor,
  │  │  original_image: Image.Image
  │  │) → np.ndarray
  │  ├─ Inputs: Tensor (1,1,60,80), PIL Image
  │  ├─ Steps:
  │  │  1. Squeeze tensor to (60, 80)
  │  │  2. Normalize to 0-255
  │  │  3. Resize to original image size (640x480)
  │  │  4. Apply colormap (COLORMAP_JET)
  │  │     - Blue for low density
  │  │     - Red for high density
  │  │  5. Convert original image to BGR
  │  │  6. Blend: 60% heatmap + 40% original
  │  │  7. Return BGR array
  │  └─ Output: np.ndarray (480x640x3) uint8 BGR
  │
  └─ predict(
     │  image: Union[str, Path, Image.Image],
     │  checkpoint_path: str = None,
     │  source: str = "image",
     │  return_density_map: bool = False
     │) → Dict
     ├─ Inputs:
     │  ├─ image: PIL Image or path
     │  ├─ source: "image"/"webcam"/"surveillance"
     │  └─ return_density_map: Include tensor in response
     ├─ Execution:
     │  1. Load config for source type
     │  2. Get max dimension from config
     │  3. Smart resize image (maintain aspect ratio)
     │  4. Get cached model
     │  5. Get preprocessor
     │  6. Preprocess: ToTensor + Normalize
     │  7. Run inference: model(tensor)
     │  8. Calculate count = density_map.sum()
     │  9. Collect timing and metadata
     │  10. Build response dict
     │  11. If return_density_map: include tensor
     │  12. Return response
     └─ Output: {
        "count": float,
        "rounded_count": int,
        "inference_time_ms": float,
        "device": str,
        "density_map_shape": tuple,
        "original_size": tuple,
        "processed_size": tuple,
        "source": str,
        "density_map": torch.Tensor (if requested)
     }
  ```

---

#### **C. csrnet.py** → Model Definition

- **File Path:** `backend/ml/src/models/csrnet/csrnet.py`
- **Purpose:** CSRNet neural network architecture
- **Class: CSRNet(nn.Module)**

  ```
  Frontend layers (VGG16-based):
  ├─ Conv(64) → Conv(64) → MaxPool
  ├─ Conv(128) → Conv(128) → MaxPool
  ├─ Conv(256) → Conv(256) → Conv(256) → MaxPool
  └─ Conv(512) → Conv(512) → Conv(512)

  Backend layers (dilated convolutions):
  ├─ Conv(512, dilation=2)
  ├─ Conv(512, dilation=2)
  ├─ Conv(512, dilation=2)
  ├─ Conv(256, dilation=2)
  ├─ Conv(128, dilation=2)
  └─ Conv(64, dilation=2)

  Output layer:
  └─ Conv(1, kernel_size=1) → ReLU

  Forward(x):
  ├─ x = frontend(x)        → (1, 512, H/8, W/8)
  ├─ x = backend(x)         → (1, 64, H/8, W/8)
  ├─ x = output_layer(x)    → (1, 1, H/8, W/8)
  └─ return ReLU(x)
  ```

- **Functions:**
  ```
  ┌─ load_csrnet(checkpoint_path, device='cpu') → CSRNet
  │  ├─ Create CSRNet instance
  │  ├─ Load state_dict from checkpoint
  │  ├─ Handle 'module.' prefix if present
  │  ├─ Move to device
  │  ├─ Set to eval mode
  │  ├─ Disable gradients
  │  └─ Return model
  │
  └─ make_layers(cfg, in_channels, batch_norm, dilation)
     └─ Constructs nn.Sequential from config list
  ```

---

### **TIER 4: ML PIPELINE INTERNALS**

#### **A. Preprocessing Module**

- **File Path:** `backend/ml/src/preprocessing/csrnet_preprocess.py`
- **CSRNetPreprocessor Class:**
  ```
  preprocess(image: PIL.Image) → torch.Tensor
  ├─ Step 1: Load config (resolution, normalization)
  ├─ Step 2: Resize image
  │  ├─ Get max dimension from config
  │  ├─ Calculate scale factor
  │  ├─ Resize using PIL.Image.BILINEAR
  │  └─ Ensure divisible by 8 (CSRNet requirement)
  ├─ Step 3: Convert PIL → NumPy array
  ├─ Step 4: ToTensor (HxWx3 → 3xHxW)
  ├─ Step 5: Normalize
  │  ├─ ImageNet mean: [0.485, 0.456, 0.406]
  │  ├─ ImageNet std: [0.229, 0.224, 0.225]
  │  └─ (x - mean) / std → floats in ~[-2, 2]
  ├─ Step 6: Add batch dimension
  └─ Return: torch.Tensor (1, 3, H, W) float32
  ```

---

#### **B. Config Loader Module**

- **File Path:** `backend/ml/src/core/config_loader.py`
- **load_csrnet_config() → Config**
  ```
  Returns configuration object with:
  ├─ preprocessing.get_dimensions(source: str)
  │  ├─ source="image" → (640, 480)
  │  ├─ source="webcam" → (640, 480)
  │  ├─ source="surveillance" → (1280, 720)
  │  └─ Returns: {length, breadth}
  ├─ model paths
  ├─ device settings
  └─ inference parameters
  ```

---

---

## 🔄 CONTROL FLOW DIAGRAM

### **User Initiates Streaming**

```
┌─────────────────────────────────────────────────────────────────┐
│ Frontend: User clicks "Start Streaming" button                  │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
                    WebcamContext.startStreaming()
                             │
         ┌───────────────────┼───────────────────┐
         ↓                   ↓                   ↓
    startWebcam()     connectWebSocket()    startInterval()
         │                   │                   │
    getUserMedia()      ws connect()       setInterval(100ms)
         │                   │                   │
   mediaStream          ws.onopen           repeated calls
         │                   │                   │
    video.play()       wsRef.current      captureAndSend()
         │                   │                   │
         └───────────────────┴───────────────────┘
                             ↓
                    setIsStreaming(true)
                             ↓
                      STATUS: "Streaming..."
```

---

### **Frame Capture & Processing Loop**

```
Every 100ms:

┌─ captureAndSend() [WebcamContext]
│
├─ Read video frame:
│  └─ videoRef.current.videoWidth/Height
│     video dimensions (e.g., 640x480)
│
├─ Create canvas:
│  └─ canvas.width = videoWidth
│     canvas.height = videoHeight
│
├─ Draw frame to canvas:
│  └─ ctx.drawImage(videoRef, 0, 0)
│     Pixel data transferred from GPU to canvas
│
├─ Encode to JPEG:
│  └─ canvas.toDataURL('image/jpeg', 0.8)
│     Browser JPEG encoder @ 80% quality
│     Result: "data:image/jpeg;base64,/9j/4AAQ..."
│     Size: ~92-123 KB per frame
│
├─ Build JSON payload:
│  └─ {
│       "frame": "data:image/jpeg;base64,...",
│       "model": "csrnet",
│       "heatmap": true,
│       "tracking": false
│     }
│
├─ Send via WebSocket:
│  └─ wsRef.current.send(JSON.stringify(payload))
│     Binary frame sent to backend
│
└─ Wait 100ms before next cycle
```

---

### **Backend Processing Pipeline**

```
┌─ websocket_count() [main.py]
│
├─ STEP 1: RECEIVE
│  └─ data = await websocket.receive_json()
│     Decode JSON from client
│
├─ STEP 2: EXTRACT
│  ├─ frame_data = data.get("frame")
│  ├─ model_type = data.get("model", "csrnet")
│  ├─ return_heatmap = data.get("heatmap", False)
│  └─ frame_number += 1
│
├─ STEP 3: DECODE BASE64
│  ├─ Split on comma: frame_data.split(",")[1]
│  └─ base64.b64decode(frame_data)
│     Result: bytes (92-122 KB JPEG)
│
├─ STEP 4: DECOMPRESS JPEG
│  ├─ Image.open(io.BytesIO(image_bytes))
│  └─ PIL reads JPEG headers and decompresses
│     Result: PIL.Image RGB (640x480 typical)
│
├─ STEP 5: MODEL SELECTION
│  └─ if model_type.lower() == "csrnet":
│     └─ Branch to CSRNet processing
│
├─ STEP 6: CALL CSRNet API
│  └─ result = csrnet_api.predict(
│       image,
│       source="webcam",
│       return_density_map=return_heatmap
│     )
│     ├─ Load config
│     ├─ Smart resize (640x480 typically)
│     ├─ Get preprocessor
│     ├─ Preprocess: ToTensor + Normalize
│     ├─ Load model (cached)
│     ├─ Forward pass: model(tensor)
│     ├─ Count = density_map.sum()
│     └─ Return {count, density_map, ...}
│
├─ STEP 7: HEATMAP GENERATION (if enabled)
│  └─ if return_heatmap and "density_map" in result:
│     └─ heatmap_overlay = csrnet_api.generate_heatmap(
│          result["density_map"],
│          original_pil_image
│        )
│        ├─ Squeeze density_map
│        ├─ Normalize to 0-255
│        ├─ Resize to original size
│        ├─ Apply JET colormap
│        ├─ Convert original to BGR
│        ├─ Blend 60% heatmap + 40% original
│        └─ Return BGR array
│
├─ STEP 8: JPEG ENCODE HEATMAP
│  └─ _, buffer = cv2.imencode('.jpg', heatmap_overlay)
│     ├─ OpenCV encodes at 85% quality
│     └─ Result: bytes (98-131 KB)
│
├─ STEP 9: BASE64 ENCODE
│  └─ img_base64 = base64.b64encode(buffer).decode()
│     ├─ Convert bytes to base64 string
│     └─ Result: "data:image/jpeg;base64,..." (~131 KB)
│
├─ STEP 10: BUILD RESPONSE
│  └─ response = {
│       "success": True,
│       "model": "csrnet",
│       "count": result["count"],
│       "rounded_count": int(round(count)),
│       "inference_time_ms": result["inference_time_ms"],
│       "frame_number": frame_number,
│       "fps": 1000 / inference_time,
│       "heatmap": "data:image/jpeg;base64,..." (if enabled)
│     }
│
├─ STEP 11: SEND RESPONSE
│  └─ await websocket.send_json(response)
│     ├─ Serialize response to JSON
│     └─ Send as binary frame over WebSocket
│
├─ STEP 12: ERROR HANDLING
│  └─ except Exception as e:
│     └─ await websocket.send_json({
│          "success": False,
│          "error": str(e)
│        })
│
└─ STEP 13: LOOP
   └─ Continue to STEP 1 (receive next frame)
```

---

## 📊 DATA FLOW BREAKDOWN

### **INPUT DATA FLOW: Frontend → Backend**

```
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: Frontend Webcam Capture                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  getUserMedia({video: {width: 640, height: 480}})          │
│  └─→ MediaStream (continuous pixel data)                   │
│      Size: 640×480 = 307,200 pixels                        │
│      Format: RGBA (8-bit per channel)                      │
│      Memory: ~900 KB per frame                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: Canvas Drawing                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  canvas.width = videoWidth                                 │
│  canvas.height = videoHeight                               │
│  ctx.drawImage(videoRef, 0, 0)                            │
│  └─→ Canvas PixelData (RGBA buffer)                        │
│      Size: 640×480×4 = 1,228,800 bytes                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: JPEG Encoding                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  canvas.toDataURL('image/jpeg', 0.8)                       │
│  ├─ Browser JPEG encoder                                  │
│  ├─ Quality: 80%                                           │
│  ├─ Color subsample: 4:2:0                                │
│  └─→ "data:image/jpeg;base64,/9j/4AAQSkZJRg..."          │
│      Encoded size: ~92 KB (compressed)                     │
│      Total with prefix: ~123 KB                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: JSON Wrapper                                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  {                                                          │
│    "frame": "data:image/jpeg;base64,..." (123 KB),        │
│    "model": "csrnet",                                      │
│    "heatmap": true,                                        │
│    "tracking": false,                                      │
│    "threshold": 0.5                                        │
│  }                                                          │
│  └─→ JSON.stringify() serialization                        │
│      Total size: ~123.5 KB                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 5: WebSocket Transmission                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  wsRef.current.send(JSON.stringify(payload))              │
│  ├─ Binary frame header: 2-14 bytes                       │
│  ├─ Payload: 123.5 KB                                     │
│  └─ Total network bytes: ~123.5 KB                        │
│     Frequency: Every 100ms (10 FPS)                        │
│     Bandwidth: ~1.235 MB/s                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓ Network
┌─────────────────────────────────────────────────────────────┐
│ STAGE 6: Backend WebSocket Reception                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  await websocket.receive_json()                            │
│  └─→ FastAPI receives binary frame                         │
│      └─→ Automatic JSON decoding                           │
│          Result: Python dict (123.5 KB in memory)          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 7: Base64 Decoding                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  frame_data = data["frame"]                                │
│  frame_data = frame_data.split(",")[1]  # Remove prefix   │
│  image_bytes = base64.b64decode(frame_data)               │
│  └─→ Result: bytes (92.2 KB JPEG)                         │
│      Format: JPEG compressed binary data                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 8: JPEG Decompression                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Image.open(io.BytesIO(image_bytes))                       │
│  ├─ PIL reads JPEG headers                                │
│  ├─ Decompresses entropy-encoded data                     │
│  ├─ YCbCr → RGB color space conversion                    │
│  └─→ PIL.Image.Image object (lazy-loaded)                 │
│      Size: 640×480 RGB                                     │
│      Format: PIL Image (metadata only ~50 KB)              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 9: Preprocessing                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Resize to model dimensions                        │
│  ├─ Get config for source="webcam"                        │
│  ├─ Max dimension: config.preprocessing.length            │
│  ├─ Aspect ratio maintained                               │
│  ├─ Divisible by 8 (CSRNet requirement)                   │
│  └─→ PIL.Image (320×240 typical)                          │
│                                                              │
│  Step 2: Convert to NumPy                                  │
│  ├─ np.array(image)                                       │
│  └─→ ndarray (240, 320, 3) uint8                          │
│      Memory: 230.4 KB                                      │
│                                                              │
│  Step 3: Normalize to [0, 1]                              │
│  ├─ array / 255                                           │
│  └─→ float32 (0.0 to 1.0)                                 │
│      Memory: 230.4 KB × 4 = 921.6 KB                      │
│                                                              │
│  Step 4: ImageNet Normalization                           │
│  ├─ mean = [0.485, 0.456, 0.406]                         │
│  ├─ std = [0.229, 0.224, 0.225]                          │
│  └─ (x - mean) / std → values ~[-2, 2]                    │
│                                                              │
│  Step 5: Convert to Tensor                                │
│  ├─ torch.from_numpy(array).float()                       │
│  ├─ Shape: (3, 240, 320) CHW format                       │
│  ├─ Add batch dim: (1, 3, 240, 320)                       │
│  └─→ torch.Tensor float32 (921.6 KB on GPU/CPU)          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### **OUTPUT DATA FLOW: Backend → Frontend**

```
┌─────────────────────────────────────────────────────────────┐
│ STAGE 10: Model Inference                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  with torch.no_grad():                                      │
│      density_map = model(tensor)                            │
│      ├─ Input: (1, 3, 240, 320) on CPU/GPU                │
│      ├─ Forward pass through CSRNet layers                │
│      ├─ Output: (1, 1, 30, 40) density map               │
│      │  (spatial dims reduced 8x per architecture)         │
│      └─ ReLU applied for non-negative values               │
│                                                              │
│  count = density_map.sum().item()                          │
│  └─→ Result: float (e.g., 45.234)                         │
│                                                              │
│  Inference time: 120-150ms (CPU)                           │
│  Memory: 19.2 KB (1×1×30×40 float32)                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 11: Heatmap Generation (if enabled)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Tensor to NumPy                                   │
│  └─ density_np = density_map.squeeze().cpu().numpy()      │
│     Result: (30, 40) float32                               │
│                                                              │
│  Step 2: Normalize to 0-255                               │
│  ├─ density_normalized = density_np / max(density_np)     │
│  ├─ * 255 → uint8                                         │
│  └─→ (30, 40) uint8 [0-255]                               │
│                                                              │
│  Step 3: Resize to original size                          │
│  ├─ cv2.resize(density, (640, 480))                       │
│  ├─ Interpolation: INTER_CUBIC                            │
│  └─→ (480, 640) uint8                                      │
│      Memory: 307.2 KB                                       │
│                                                              │
│  Step 4: Apply colormap (JET)                             │
│  ├─ cv2.applyColorMap(density, COLORMAP_JET)             │
│  ├─ Maps intensity → BGR colors:                          │
│  │  ├─ 0 (min) → Blue (low density)                       │
│  │  ├─ 128 (mid) → Green/Yellow (medium)                  │
│  │  └─ 255 (max) → Red (high density)                     │
│  └─→ (480, 640, 3) uint8 BGR                              │
│      Memory: 921.6 KB                                       │
│                                                              │
│  Step 5: Convert original to BGR                          │
│  ├─ cv2.cvtColor(image, COLOR_RGB2BGR)                    │
│  └─→ (480, 640, 3) uint8 BGR                              │
│                                                              │
│  Step 6: Blend images                                      │
│  ├─ cv2.addWeighted(original, 0.4, heatmap, 0.6, 0)      │
│  ├─ Formula: 0.4×original + 0.6×heatmap                   │
│  └─→ (480, 640, 3) uint8 BGR                              │
│      Result shows heatmap overlay on original image        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 12: JPEG Encoding Heatmap                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  _, buffer = cv2.imencode('.jpg', heatmap_overlay)        │
│  ├─ OpenCV JPEG encoder                                   │
│  ├─ Quality: 85% (IMWRITE_JPEG_QUALITY default)           │
│  ├─ Compression: Lossy (3.6 MB → 98.5 KB)                │
│  └─→ buffer (numpy array of bytes)                        │
│      Memory: 98.5 KB                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 13: Base64 Encoding Heatmap                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  base64.b64encode(buffer).decode()                         │
│  ├─ Converts 98.5 KB bytes → base64 string                │
│  ├─ Expansion: 98.5 KB × 1.33 = 131 KB                   │
│  └─→ "/9j/4AAQSkZJRg..." (131 KB string)                 │
│                                                              │
│  f"data:image/jpeg;base64,{img_base64}"                    │
│  └─→ "data:image/jpeg;base64,/9j/4AAQ..." (131 KB)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 14: Response JSON Building                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  response = {                                               │
│    "success": true,                                         │
│    "model": "csrnet",                                       │
│    "count": 45,              ← From density_map.sum()      │
│    "rounded_count": 45,      ← int(round(count))           │
│    "inference_time_ms": 125.3,  ← Timing measurement       │
│    "frame_number": 127,      ← Request counter             │
│    "fps": 7.95,              ← 1000/inference_time         │
│    "heatmap": "data:image/jpeg;base64,..." ← If enabled   │
│  }                                                          │
│  └─→ Dict size: ~131.1 KB                                  │
│      (mostly heatmap, small metrics)                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 15: WebSocket Response Send                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  await websocket.send_json(response)                        │
│  ├─ FastAPI serializes dict to JSON                        │
│  ├─ Encodes as WebSocket binary frame                      │
│  ├─ Sends over network connection                          │
│  └─→ Total over wire: ~131.1 KB                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓ Network
┌─────────────────────────────────────────────────────────────┐
│ STAGE 16: Frontend WebSocket Reception                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ws.onmessage = (event) => {                                │
│    const data = JSON.parse(event.data)                     │
│    └─→ Automatic WebSocket + JSON decoding                 │
│        Result: JavaScript object (~131.1 KB)               │
│  }                                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 17: React State Update                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Update 1: setCount(Math.round(data.count))                │
│  ├─ State: count = 45                                      │
│  └─ Component re-render 1                                  │
│                                                              │
│  Update 2: setFps(data.fps)                                │
│  ├─ State: fps = 7.95                                      │
│  └─ Component re-render 2                                  │
│                                                              │
│  Update 3: setInferenceTime(...)                           │
│  ├─ State: inferenceTime = 125.3                           │
│  └─ Component re-render 3                                  │
│                                                              │
│  Update 4: setResults(data)                                │
│  ├─ State: results = {full response}                       │
│  └─ Component re-render 4                                  │
│                                                              │
│  Update 5: if (data.heatmap)                               │
│  │           setHeatmapImage(data.heatmap)                │
│  ├─ State: heatmapImage = "data:image/jpeg;base64,..."   │
│  └─ Component re-render 5 (triggers image decode)          │
│                                                              │
│  Update 6: setStatus(...)                                  │
│  ├─ State: status = "Processing - Count: 45..."            │
│  └─ Component re-render 6                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 18: React Component Rendering                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Webcam.js re-renders with updated props from context      │
│  └─ <div className="count-display">                        │
│     └─ Count: {count}  ← "45" displayed                    │
│                                                              │
│  <div className="fps-display">                             │
│  └─ FPS: {fps}  ← "7.95" displayed                         │
│                                                              │
│  <HeatmapCard heatmapImage={heatmapImage} />               │
│  └─ <img src={heatmapImage} />                             │
│     src: "data:image/jpeg;base64,..." (131 KB)             │
│                                                              │
│  <CSRNetCard results={results} />                          │
│  └─ <pre>{JSON.stringify(results, null, 2)}</pre>         │
│     Displays full JSON response                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 19: Browser Image Rendering                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  <img src="data:image/jpeg;base64,..." />                  │
│  ├─ Browser image decoder                                  │
│  ├─ Base64 decode: 131 KB → 98.5 KB JPEG                 │
│  ├─ JPEG decompress: 98.5 KB → 3.6 MB bitmap             │
│  ├─ Send to GPU for rendering                             │
│  └─→ Displayed on screen ✅                                 │
│      User sees: Heatmap with crowd density visualization   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 WEBSOCKET COMMUNICATION

### **Request Message Format**

```json
{
  "frame": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
  "model": "csrnet",
  "heatmap": true,
  "tracking": false,
  "threshold": 0.5
}
```

**Message Size:** ~123.5 KB  
**Frequency:** Every 100ms  
**Bandwidth:** 1.235 MB/s @ 10 FPS

### **Response Message Format**

```json
{
  "success": true,
  "model": "csrnet",
  "count": 45.234,
  "rounded_count": 45,
  "inference_time_ms": 125.3,
  "frame_number": 127,
  "fps": 7.95,
  "heatmap": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA..."
}
```

**Message Size:** ~131.1 KB  
**Latency:** 125-150ms (CPU inference)

---

## 🧠 BACKEND PROCESSING

### **CSRNet Model Processing Steps**

```
1. CONFIG LOADING
   ├─ Source: "webcam"
   └─ Get max_dimension from config
      └─ Returns dimensions config

2. IMAGE RESIZING
   ├─ Input: PIL.Image (640×480)
   ├─ Calculate scale to fit max_dimension
   ├─ Resize maintaining aspect ratio
   ├─ Ensure divisible by 8
   └─ Output: PIL.Image (320×240 typical)

3. PREPROCESSING
   ├─ np.array() convert
   ├─ Normalize to [0, 1]
   ├─ ImageNet normalization
   ├─ torch.Tensor conversion
   └─ Add batch dimension

4. MODEL LOADING
   ├─ Check cache
   ├─ If not cached: load from checkpoint
   ├─ Move to CPU device
   ├─ Set eval mode
   └─ Disable gradients

5. INFERENCE
   ├─ Forward pass through CSRNet
   ├─ Output: density_map (1, 1, 30, 40)
   ├─ Sum all values: count
   └─ No backprop (eval mode)

6. HEATMAP GENERATION (optional)
   ├─ Squeeze density tensor
   ├─ Normalize to 0-255
   ├─ Resize to original size
   ├─ Apply JET colormap
   ├─ Blend with original image
   └─ Encode to JPEG + Base64

7. RESPONSE BUILDING
   ├─ Collect metrics
   ├─ Build JSON dict
   └─ Return to client
```

---

## 💾 FRONTEND STATE MANAGEMENT

### **WebcamContext State Variables**

| Variable         | Type    | Purpose                      |
| ---------------- | ------- | ---------------------------- |
| `isStreaming`    | boolean | Stream active status         |
| `selectedModel`  | string  | Current model name           |
| `enableTracking` | boolean | Tracking enabled flag        |
| `enableHeatmap`  | boolean | Heatmap visualization toggle |
| `count`          | number  | Crowd count estimate         |
| `fps`            | number  | Frames per second processed  |
| `inferenceTime`  | number  | Model inference latency (ms) |
| `heatmapImage`   | string  | Base64 heatmap image URL     |
| `densityStats`   | object  | Density map statistics       |
| `error`          | string  | Error message                |
| `status`         | string  | Current operation status     |
| `results`        | object  | Full backend response        |

### **Component State Updates**

```
WebSocket onmessage
    ↓
JSON.parse(event.data)
    ↓
if (data.success)
    ├─→ setCount(data.count)
    ├─→ setFps(data.fps)
    ├─→ setInferenceTime(data.inference_time_ms)
    ├─→ setResults(data)
    ├─→ if (data.heatmap): setHeatmapImage(data.heatmap)
    ├─→ if (data.density_map_stats): setDensityStats(...)
    ├─→ setStatus("Processing - Count: 45...")
    └─→ setError(null)
else
    └─→ setError(data.error)
```

---

## 🔗 COMPONENT CALL HIERARCHY

```
App.js
├─ Imports: Webcam component
└─ Renders: <Webcam currentModel={currentModel} />

Webcam.js (Page)
├─ Imports: useWebcam() hook
├─ Uses: WebcamContext state
├─ Renders: Layout with:
│  ├─ <Nav> - Navigation
│  ├─ <Menu> - Left sidebar
│  ├─ Main content:
│  │  ├─ Status panel
│  │  ├─ <video ref={videoRef}>
│  │  ├─ <canvas ref={canvasRef}>
│  │  ├─ <HeatmapCard heatmapImage={heatmapImage} />
│  │  └─ <CSRNetCard results={results} />
│  └─ <RightMenu> - Control panel

WebcamContext.js (Provider)
├─ State: All streaming variables
├─ Refs: videoRef, canvasRef, wsRef, streamRef, intervalRef
├─ Functions:
│  ├─ connectWebSocket()
│  ├─ startWebcam()
│  ├─ captureAndSend()
│  ├─ startStreaming()
│  └─ stopEverything()
└─ Exports: useWebcam() hook

Main.py (Backend)
├─ FastAPI app instance
├─ WebSocket handler: @app.websocket("/ws/count")
├─ Receives JSON frame
├─ Calls model APIs
└─ Returns JSON response

CSRNet API (ml/src/models/csrnet/api.py)
├─ get_model() - Returns cached model
├─ get_preprocessor() - Returns transforms
├─ generate_heatmap() - Creates overlay image
└─ predict() - Main prediction function
   ├─ Load config
   ├─ Resize image
   ├─ Preprocess tensor
   ├─ Call model
   └─ Return metrics + density_map

CSRNet Model (ml/src/models/csrnet/csrnet.py)
├─ Class: CSRNet(nn.Module)
├─ load_csrnet() - Load checkpoint
└─ Forward pass: Density map generation
```

---

## ⚡ PERFORMANCE METRICS

| Component                  | Time           | Size     | Notes              |
| -------------------------- | -------------- | -------- | ------------------ |
| Canvas encoding (Frontend) | 5-10ms         | 123 KB   | Per-frame JPEG     |
| WebSocket transmission     | 50-100ms       | 123 KB   | Network latency    |
| Backend reception          | <1ms           | 123 KB   | JSON parsing       |
| Base64 decode              | 2-3ms          | 92.2 KB  | CPU operation      |
| JPEG decompress            | 5-8ms          | -        | PIL decompression  |
| Preprocessing              | 20-30ms        | 921.6 KB | Tensor conversion  |
| CSRNet inference (CPU)     | 120-150ms      | 19.2 KB  | Model computation  |
| Heatmap generation         | 15-25ms        | 921.6 KB | OpenCV operations  |
| JPEG encoding heatmap      | 10-15ms        | 98.5 KB  | cv2.imencode       |
| Base64 encode              | 2-3ms          | 131 KB   | String conversion  |
| WebSocket response send    | 50-100ms       | 131 KB   | Network latency    |
| Frontend state update      | 5-10ms         | -        | React re-render    |
| Browser image decode       | 10-20ms        | 3.6 MB   | Display rendering  |
| **Total pipeline latency** | **~400-500ms** | -        | Request to display |

---

**Pipeline Documentation Complete**  
**Last Updated:** November 25, 2025  
**All components mapped and documented**
