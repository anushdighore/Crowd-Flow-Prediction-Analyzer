# 📊 DATA FLOW REPORT - Complete Transformation Analysis

**Project:** Crowd Flow Prediction Analyzer  
**Generated:** November 25, 2025  
**Scope:** Raw frame → Canvas → Base64 → WebSocket → Backend → ML → Response → Frontend

---

## 📑 TABLE OF CONTENTS

1. [Complete Data Transformation Pipeline](#complete-data-transformation-pipeline)
2. [Frame Encoding/Decoding](#frame-encodingdecoding)
3. [WebSocket Message Formats](#websocket-message-formats)
4. [Model-Specific Output Data](#model-specific-output-data)
5. [Response Data Structures](#response-data-structures)
6. [Data Mismatches & Breakpoints](#data-mismatches--breakpoints)
7. [Frontend State Updates](#frontend-state-updates)

---

## 🔄 COMPLETE DATA TRANSFORMATION PIPELINE

### High-Level Data Flow

```mermaid
graph LR
    A["🎥 Webcam<br/>Real-time stream"] -->|getUserMedia| B["📹 Video Element<br/>HTMLVideoElement"]
    B -->|drawImage| C["🖼️ Canvas<br/>640x480 pixels"]
    C -->|toDataURL| D["🔤 Base64 String<br/>data:image/jpeg;base64,..."]
    D -->|JSON Payload| E["📡 WebSocket<br/>Send to backend"]
    E -->|Receive bytes| F["🔌 Backend<br/>FastAPI WebSocket"]
    F -->|base64.b64decode| G["🖼️ BytesIO<br/>Raw bytes"]
    G -->|Image.open| H["🎨 PIL Image<br/>RGB mode"]
    H -->|np.array| I["📊 NumPy Array<br/>HxWx3 uint8"]
    I -->|Preprocess| J["🔧 Tensor<br/>Normalized floats"]
    J -->|Model Inference| K["🤖 ML Model<br/>GPU/CPU processing"]
    K -->|Output| L["📈 Density Map/<br/>Bounding Boxes"]
    L -->|Post-process| M["📊 Count + Metrics"]
    L -->|Visualization| N["🎨 Heatmap Image"]
    M -->|JSON Response| O["📦 WebSocket<br/>Send back to frontend"]
    N -->|Base64 encode| O
    O -->|Parse JSON| P["💾 Frontend State<br/>React Context"]
    P -->|setCount/setHeatmap| Q["🖥️ Component Re-render<br/>Display results"]
```

### Step-by-Step Byte-Level Transformation

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: WEBCAM CAPTURE (Frontend)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Webcam Hardware                                                 │
│      ↓                                                           │
│  getUserMedia() → MediaStream                                   │
│  Props: {video: {width: 640, height: 480}, audio: false}       │
│      ↓                                                           │
│  <video autoplay playsinline muted ref={videoRef} />            │
│  Size: 640x480 pixels = 307,200 pixels                         │
│  Memory: ~900 KB per frame (RGB 8-bit per channel)             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: CANVAS CAPTURE (Frontend)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Every 100ms:                                                   │
│  ctx.drawImage(videoRef.current, 0, 0)                         │
│  ↓                                                              │
│  Canvas 2D Context holds pixel data                             │
│  Format: RGBA (640x480x4 = 1,228,800 bytes in memory)         │
│  Visual: Exact copy of video frame at capture moment           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: JPEG ENCODING (Frontend)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  canvas.toDataURL('image/jpeg', 0.8)  ← 80% quality            │
│  ↓                                                              │
│  JPEG Encoder (browser's built-in)                              │
│  ├─ Quality: 0.8 = 80% compression                             │
│  ├─ Color subsam: 4:2:0 (standard JPEG)                        │
│  ├─ Motion compression: Not applicable (single frame)          │
│  └─ Result: ~92 KB per frame (typical)                         │
│  ↓                                                              │
│  Returns: "data:image/jpeg;base64,/9j/4AAQSkZJRg..."          │
│  Length: 92 KB × 1.33 (base64 overhead) = ~122 KB              │
│                                                                  │
│  Data URI Format:                                               │
│  ├─ Prefix: "data:image/jpeg;base64,"  (30 bytes)              │
│  ├─ Base64 payload: 122,880 bytes                               │
│  └─ Total string length: ~123 KB                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: JSON PAYLOAD (Frontend)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  {                                                               │
│    "frame": "data:image/jpeg;base64,/9j/4AAQ...",  ← 123 KB    │
│    "model": "csrnet",                              ← 8 bytes    │
│    "tracking": false,                              ← 5 bytes    │
│    "heatmap": true,                                ← 4 bytes    │
│    "threshold": 0.5                                ← 3 bytes    │
│  }                                                              │
│                                                                  │
│  JSON serialized: {frame: "...", model: "csrnet", ...}         │
│  Total size: ~123.5 KB (mostly frame data)                     │
│                                                                  │
│  WebSocket send (binary frame):                                │
│  ├─ Frame header: 2-14 bytes (WebSocket protocol)             │
│  ├─ Payload: 123.5 KB                                          │
│  └─ Total over network: ~123.5 KB                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓ Network transmission
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: BACKEND RECEPTION (FastAPI)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WebSocket frame received (123.5 KB)                            │
│  ↓                                                              │
│  JSON decoded by FastAPI:                                       │
│  {                                                               │
│    "frame": "data:image/jpeg;base64,/9j/4AAQ...",             │
│    "model": "csrnet",                                          │
│    "heatmap": true                                             │
│  }                                                              │
│                                                                  │
│  Extract: frame_data = payload["frame"]                        │
│  String in Python: str type, 123.5 KB in memory               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 6: BASE64 DECODING (Backend)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: "data:image/jpeg;base64,/9j/4AAQ..."  (123.5 KB)      │
│  ↓                                                              │
│  Remove prefix: frame_data.split(",")[1]                       │
│  Result: "/9j/4AAQ..." (122.9 KB base64)                       │
│  ↓                                                              │
│  base64.b64decode(frame_data)  [Python function]               │
│  ├─ Converts each 4 base64 chars → 3 bytes                     │
│  ├─ Input: 122,880 base64 chars                                │
│  └─ Output: ~92.2 KB raw JPEG bytes                            │
│  ↓                                                              │
│  Result: bytes object, 92.2 KB in memory                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 7: JPEG DECOMPRESSION (Backend)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: bytes (92.2 KB JPEG data)                              │
│  ↓                                                              │
│  Image.open(io.BytesIO(image_bytes))  [PIL function]           │
│  ├─ Reads JPEG headers                                         │
│  ├─ Decodes entropy-encoded data                               │
│  ├─ Performs YCbCr → RGB color space conversion                │
│  └─ Result: PIL.Image object (metadata only)                   │
│  ↓                                                              │
│  PIL.Image in memory: ~50 KB (lazy loading)                    │
│  Image size: 640x480 pixels                                    │
│  Format: "JPEG"                                                │
│  Mode: "RGB" after convert('RGB')                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 8: MODEL PREPROCESSING (Backend)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CSRNet preprocessing:                                          │
│  ↓                                                              │
│  1. Resize image (640x480) → (320x240)  [config-driven]       │
│     PIL.Image.resize() → 320x240 pixels                        │
│  ↓                                                              │
│  2. Convert to numpy array:                                    │
│     np.array(image) → ndarray shape (240, 320, 3), uint8      │
│     Memory: 230.4 KB                                           │
│  ↓                                                              │
│  3. Normalize:                                                 │
│     Divide by 255 → float32  [0.0 - 1.0]                      │
│     Memory: 230.4 KB × 4 bytes (float32) = 921.6 KB           │
│  ↓                                                              │
│  4. Apply ImageNet normalization:                              │
│     (x - mean) / std                                           │
│     mean = [0.485, 0.456, 0.406]                              │
│     std = [0.229, 0.224, 0.225]                               │
│  ↓                                                              │
│  5. Convert to tensor:                                         │
│     torch.from_numpy(array).float()                            │
│     Shape: (3, 240, 320)  [CHW format]                         │
│     Memory: 921.6 KB on GPU/CPU                                │
│  ↓                                                              │
│  Final preprocessed tensor: (1, 3, 240, 320)  [batch dim]     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 9: MODEL INFERENCE (GPU/CPU)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CSRNet Forward Pass:                                           │
│  ↓                                                              │
│  Input: tensor (1, 3, 240, 320)                               │
│  Device: CPU (forced for memory safety)                        │
│  ↓                                                              │
│  Network:                                                      │
│  ├─ Conv layers (dilated, cascaded architecture)             │
│  ├─ Generates density map at multiple scales                  │
│  └─ Final output: (1, 1, 60, 80)  [downsampled 8x]           │
│  ↓                                                              │
│  Inference time: 120-150ms (CPU), 8-12ms (GPU)               │
│  ↓                                                              │
│  Output: density_map tensor                                   │
│  ├─ Shape: (1, 1, 60, 80) = 4,800 values                     │
│  ├─ Dtype: float32                                            │
│  ├─ Range: [0.0 to ~max_count_per_pixel]                     │
│  └─ Memory: 19.2 KB                                           │
│                                                                  │
│  Crowd Count Calculation:                                      │
│  count = density_map.sum().item()  ← Sums all values         │
│  Result: float (e.g., 45.234)                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 10: HEATMAP GENERATION (Backend)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT: density_map tensor (1, 1, 60, 80)                     │
│                                                                  │
│  Step 1: Tensor to NumPy                                      │
│  ├─ density_map.squeeze() → (60, 80)                         │
│  ├─ .cpu().detach().numpy()                                   │
│  └─ Result: ndarray (60, 80) float32                         │
│                                                                  │
│  Step 2: Normalize to 0-255                                   │
│  ├─ min_val = density_map.min()                              │
│  ├─ max_val = density_map.max()                              │
│  ├─ normalized = (density_map - min_val) / (max_val - min_val)
│  ├─ normalized * 255 → uint8                                 │
│  └─ Result: ndarray (60, 80) uint8  [0-255]                 │
│                                                                  │
│  Step 3: Resize to Original Image Size                        │
│  ├─ cv2.resize(density_normalized, (640, 480))              │
│  │  Interpolation: INTER_CUBIC (high quality)               │
│  └─ Result: ndarray (480, 640) uint8                        │
│                                                                  │
│  Step 4: Apply Colormap (JET)                                │
│  ├─ cv2.applyColorMap(density_resized, cv2.COLORMAP_JET)    │
│  ├─ Maps grayscale → BGR colors:                            │
│  │  ├─ 0 (black) → Blue (low density)                       │
│  │  ├─ 128 (gray) → Green/Yellow (medium)                   │
│  │  └─ 255 (white) → Red (high density)                     │
│  └─ Result: ndarray (480, 640, 3) uint8 BGR                 │
│                                                                  │
│  Step 5: Blend with Original Image                            │
│  ├─ cv2.cvtColor(image, COLOR_RGB2BGR) → BGR original       │
│  ├─ cv2.addWeighted(original_bgr, 0.4, heatmap, 0.6, 0)     │
│  │  overlay = 0.4 * original + 0.6 * heatmap                │
│  │  (40% original photo, 60% colored heatmap)               │
│  └─ Result: ndarray (480, 640, 3) uint8 BGR                 │
│                                                                  │
│  Memory at each step:                                         │
│  ├─ Density tensor: 19.2 KB                                  │
│  ├─ Resized density: 1.22 MB                                 │
│  ├─ Colormap applied: 3.6 MB                                 │
│  ├─ Overlay blended: 3.6 MB                                  │
│  └─ Peak: ~3.6 MB during processing                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 11: HEATMAP ENCODING (Backend)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT: ndarray (480, 640, 3) uint8 BGR [3.6 MB raw]        │
│  ↓                                                              │
│  cv2.imencode('.jpg', heatmap_overlay)                        │
│  ├─ Encodes to JPEG format                                   │
│  ├─ Quality: 85 (default IMWRITE_JPEG_QUALITY)              │
│  ├─ Compression: Significant (lossless RGB → lossy JPEG)    │
│  └─ Result: buffer (JPEG bytes), ~98.5 KB                    │
│  ↓                                                              │
│  base64.b64encode(buffer)                                     │
│  ├─ Converts binary bytes to base64 string                   │
│  ├─ Expansion: 98.5 KB × 1.33 = ~131 KB                     │
│  └─ Result: base64 string                                    │
│  ↓                                                              │
│  f"data:image/jpeg;base64,{img_base64}"                       │
│  └─ Final: "data:image/jpeg;base64,/9j/4AAQ..." (131 KB)    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 12: RESPONSE JSON (Backend)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Build response dictionary:                                    │
│  {                                                               │
│    "success": true,                          ← 4 bytes        │
│    "model": "csrnet",                        ← 8 bytes        │
│    "count": 45.234,                          ← 5 bytes        │
│    "inference_time_ms": 125.3,               ← 5 bytes        │
│    "frame_number": 127,                      ← 3 bytes        │
│    "fps": 7.95,                              ← 4 bytes        │
│    "heatmap": "data:image/jpeg;base64,..."   ← 131 KB        │
│  }                                                              │
│                                                                  │
│  JSON serialized: json.dumps(response)                         │
│  ├─ String representation of dict                             │
│  ├─ All values quoted/formatted                               │
│  └─ Total size: ~131.1 KB (mostly heatmap)                    │
│                                                                  │
│  WebSocket send (binary frame):                               │
│  ├─ Frame header: 2-14 bytes                                 │
│  ├─ Payload: 131.1 KB (JSON text)                            │
│  └─ Total over network: ~131.1 KB                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓ Network transmission
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 13: FRONTEND RECEPTION (React)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WebSocket.onmessage(event)                                    │
│  ├─ event.data: String (131.1 KB JSON)                       │
│  └─ Received via JS string                                    │
│  ↓                                                              │
│  JSON.parse(event.data)                                       │
│  ├─ Converts JSON string → JavaScript object                 │
│  ├─ All fields extracted as properties                       │
│  └─ heatmap property: "data:image/jpeg;base64,..."           │
│  ↓                                                              │
│  Destructure: const { heatmap, count, fps } = data          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 14: STATE UPDATE (React Context)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  if (data.heatmap) {                                            │
│    setHeatmapImage(data.heatmap)                              │
│    ↓                                                            │
│    React state update:                                         │
│    heatmapImage: "data:image/jpeg;base64,..." (131 KB)       │
│    ↓                                                            │
│    Component re-render triggered                               │
│  }                                                              │
│                                                                  │
│  setCount(data.count)                                          │
│  ├─ count: 45 (number)                                        │
│  └─ Component re-render                                        │
│                                                                  │
│  setFps(data.fps)                                              │
│  └─ fps: 7.95 (number)                                        │
│                                                                  │
│  setResults(data)                                              │
│  └─ Full response object in state                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 15: COMPONENT RENDER (React)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Webcam.js render() function called                            │
│  ├─ Props: from useWebcam() hook                              │
│  ├─ State: CSS styles, layout                                 │
│  └─ Dependencies: count, fps, heatmapImage                    │
│  ↓                                                              │
│  JSX elements created:                                         │
│  ├─ <div> Status Panel                                        │
│  │  ├─ Count: {count} = "45"  ← text node                    │
│  │  ├─ FPS: {fps} = "7.95"    ← text node                    │
│  │  └─ Model: "CSRNet"                                        │
│  │                                                             │
│  ├─ <HeatmapCard>                                             │
│  │  ├─ <img src={heatmapImage} />                            │
│  │  │  src attribute = "data:image/jpeg;base64,..."         │
│  │  │  Browser decodes and displays heatmap image            │
│  │  └─ Rendered as <img> element                             │
│  │                                                             │
│  └─ <CSRNetCard>                                              │
│     └─ <pre>{JSON.stringify(results, null, 2)}</pre>        │
│        └─ Raw JSON pretty-printed                            │
│                                                                  │
│  Rendered DOM:                                                 │
│  └─ <div class="status-panel">                                │
│     ├─ <div>Count: 45</div>                                  │
│     ├─ <div>FPS: 7.95</div>                                  │
│     └─ <img src="data:image/jpeg;base64,..." />             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 16: BROWSER RENDERING (HTML5)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  <img src="data:image/jpeg;base64,..." />                     │
│  ↓                                                              │
│  Browser Image Decoder:                                        │
│  ├─ Receives base64 string                                    │
│  ├─ Decodes base64 → JPEG bytes (98.5 KB)                   │
│  ├─ Decompresses JPEG → bitmap (3.6 MB raw)                 │
│  ├─ Scales to CSS display size (let's say 640x480)          │
│  └─ Sends to GPU for rendering                               │
│  ↓                                                              │
│  GPU Rendering:                                               │
│  ├─ Compositing with other layers                            │
│  ├─ Anti-aliasing, filtering                                 │
│  └─ Blits to screen framebuffer                              │
│  ↓                                                              │
│  RESULT: Heatmap displayed on screen ✅                       │
│  └─ User sees red=high density, blue=low density            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔤 FRAME ENCODING/DECODING

### Canvas Encoding

```javascript
// Encoding chain
canvas.toDataURL('image/jpeg', 0.8)
  ├─ Reads canvas pixel buffer (RGBA, 640x480x4 = 1.228 MB)
  ├─ Downsamples to RGB (removes alpha)
  ├─ Applies JPEG compression at 80% quality
  ├─ Base64 encodes result (~92 KB)
  └─ Returns: "data:image/jpeg;base64,/9j/4AAQSkZJRg..." (~123 KB)

// Time cost
Canvas encoding: ~5-10ms per frame
```

### Backend Decoding

```python
# Decoding chain
frame_data = "data:image/jpeg;base64,/9j/4AAQSkZJRg..."

# Extract base64 part
frame_data = frame_data.split(",")[1]  # Remove prefix
# frame_data = "/9j/4AAQSkZJRg..." (~122.9 KB)

# Decode base64 → JPEG bytes
import base64
image_bytes = base64.b64decode(frame_data)
# image_bytes = b'\xff\xd8\xff\xe0...' (~92.2 KB)

# Decompress JPEG → RGB image
from PIL import Image
import io
image = Image.open(io.BytesIO(image_bytes))
# image = PIL.Image.Image
# size: 640x480
# mode: "JPEG" → convert to "RGB" if needed

# Time cost
Base64 decode: ~2-3ms
JPEG decompress: ~5-8ms
Total: ~7-11ms
```

---

## 📡 WEBSOCKET MESSAGE FORMATS

### Frontend → Backend (Request)

```json
{
  "frame": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "model": "csrnet",
  "tracking": false,
  "heatmap": true,
  "threshold": 0.5
}
```

**Message Size:** ~123.5 KB (mostly frame data)

**Frequency:** Every 100ms = 10 frames per second

**Network Usage:** ~1.235 MB/s with 10 FPS

### Backend → Frontend (Response) - CSRNet with Heatmap

```json
{
  "success": true,
  "model": "csrnet",
  "count": 45.234,
  "rounded_count": 45,
  "inference_time_ms": 125.3,
  "frame_number": 127,
  "fps": 7.95,
  "heatmap": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Message Size:** ~131.1 KB (heatmap dominant)

### Backend → Frontend (Response) - YOLO with Boxes

```json
{
  "success": true,
  "model": "yolo-nano",
  "count": 3,
  "boxes": [
    { "x1": 150, "y1": 200, "x2": 300, "y2": 450, "confidence": 0.95 },
    { "x1": 350, "y1": 100, "x2": 500, "y2": 350, "confidence": 0.92 },
    { "x1": 550, "y1": 250, "x2": 640, "y2": 480, "confidence": 0.88 }
  ],
  "average_confidence": 0.917,
  "inference_time_ms": 8.5,
  "fps": 117.6,
  "heatmap": "data:image/jpeg;base64,..."
}
```

**Message Size:** ~131.5 KB (heatmap if enabled)

---

## 🤖 MODEL-SPECIFIC OUTPUT DATA

### CSRNet Output Structure

```python
{
    # Core counting metrics
    "count": 45.234,                              # float
    "rounded_count": 45,                          # int

    # Performance metrics
    "inference_time_ms": 125.3,                   # float
    "device": "cpu",                              # str (cpu|cuda)

    # Image metadata
    "original_size": (640, 480),                  # tuple (W, H)
    "processed_size": (320, 240),                 # tuple (W, H)
    "source": "webcam",                           # str

    # Density map (if requested)
    "density_map": <torch.Tensor>,                # torch.Tensor (1,1,60,80)

    # Additional statistics
    "density_map_shape": (60, 80),
    "density_map_stats": {
        "min": 0.0,
        "max": 0.85,
        "mean": 0.12,
        "sum": 45.234
    }
}
```

### YOLO Output Structure

```python
{
    # Core detection metrics
    "count": 3,                                   # int
    "rounded_count": 3,                          # int

    # Detection results
    "boxes": [
        {
            "x1": 150,                            # int (pixel)
            "y1": 200,                            # int (pixel)
            "x2": 300,                            # int (pixel)
            "y2": 450,                            # int (pixel)
            "confidence": 0.95                    # float [0-1]
        },
        # ... more boxes
    ],

    # Confidence statistics
    "confidence_stats": {
        "min": 0.88,
        "max": 0.95,
        "mean": 0.917
    },

    # Performance metrics
    "inference_time_ms": 8.5,                    # float
    "device": "cuda",                            # str

    # Image metadata
    "original_size": (640, 480),                 # tuple (W, H)
    "source": "webcam",                          # str

    # Visualization (if requested)
    "annotated_image": <np.ndarray>,             # BGR uint8 (480,640,3)
}
```

### TMTB (VMamba) Output Structure

```python
{
    # Similar to CSRNet
    "count": 45.234,
    "rounded_count": 45,
    "inference_time_ms": 142.7,
    "device": "cpu",
    "original_size": (640, 480),
    "processed_size": (384, 384),
    "source": "webcam",
    "density_map": <torch.Tensor>,               # (1,1,48,48)
    # ... other CSRNet fields
}
```

### UnifiedCounter (Tracking) Output Structure

```python
{
    # Core metrics
    "count": 3,                                  # int
    "unique_count": 3,                          # int (unique IDs tracked)

    # Tracking data
    "tracks": [
        {
            "id": 1,
            "bbox": [150, 200, 300, 450],
            "confidence": 0.95,
            "trajectory": [[150,200], [152,202], [154,204]],
            "speed": 1.5,                        # pixels/frame
            "direction": "right"
        },
        # ... more tracks
    ],

    # Statistics
    "speed_stats": {
        "avg": 1.3,
        "min": 0.5,
        "max": 2.1,
        "unit": "pixels/frame"
    },

    # Advanced metrics
    "advanced_metrics": {
        "crowd_density": "medium",
        "flow_direction": "right",
        "congestion_level": 0.4,
        "avg_crowd_velocity": 1.5
    },

    # Performance
    "inference_time_ms": 12.3,
    "tracking_time_ms": 3.2,
    "total_time_ms": 15.5
}
```

---

## 📦 RESPONSE DATA STRUCTURES

### Successful WebSocket Response

```json
{
  "success": true,
  "model": "csrnet",
  "count": 45,
  "inference_time_ms": 125.3,
  "frame_number": 127,
  "fps": 7.95,
  "heatmap": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

### Error Response

```json
{
  "success": false,
  "error": "No frame data received"
}
```

or

```json
{
  "success": false,
  "error": "Model inference failed: CUDA out of memory"
}
```

### REST API Response (CSRNet)

```json
{
  "status": "success",
  "count": 45,
  "raw_count": 45.234,
  "inference_time_ms": 125.3,
  "device": "cpu",
  "original_size": [640, 480],
  "processed_size": [320, 240],
  "heatmap": "data:image/jpeg;base64,..." // if requested
}
```

---

## ❌ DATA MISMATCHES & BREAKPOINTS

### Breakpoint 1: Heatmap Flag Not Sent

**Problem:**

```javascript
// Frontend sends heatmap: false
{
  frame: "...",
  model: "csrnet",
  heatmap: false  ← User disabled
}
```

**Backend Impact:**

```python
return_heatmap = False
result = csrnet_api.predict(..., return_density_map=False)
# density_map NOT in result
```

**Result:** No heatmap in response ✅ (correct behavior)

---

### Breakpoint 2: Model Type Mismatch

**Problem:**

```javascript
// Frontend sends model with typo
{
  model: "csrnet_vx"  ← Invalid model name
}
```

**Backend Impact:**

```python
model_type = "csrnet_vx"
# Not in yolo_model_map
# Not equal to "tmtb"
# Falls through to default CSRNet
# Actually works! ✅ (fallback is good)
```

---

### Breakpoint 3: Density Map Not Returned

**Problem:**

```python
# CSRNet called with return_density_map=True
result = csrnet_api.predict(..., return_density_map=True)

# But api.py doesn't respect the flag
# (hypothetical bug)
# density_map NOT in result
```

**Backend Impact:**

```python
if return_heatmap and "density_map" in result:
    # Condition fails → no heatmap generated
    # response["heatmap"] field missing
```

**Frontend Impact:**

```javascript
if (data.heatmap) {
  setHeatmapImage(data.heatmap); // Skipped
}
// heatmapImage stays null
// No heatmap displayed ❌ (user enabled it but nothing shows)
```

---

### Breakpoint 4: JPEG Encoding Fails

**Problem:**

```python
# Heatmap overlay failed to encode
cv2.imencode('.jpg', heatmap_overlay)
# Raised exception → caught
# response["heatmap"] not set
```

**Frontend Impact:**

```javascript
console.log("⚠️ No heatmap in backend response");
// But user enabled it
// Expected heatmap, got nothing ❌
```

---

### Breakpoint 5: Base64 Decoding Fails

**Problem:**

```javascript
// Frontend sends malformed base64
{
  frame: "data:image/jpeg;base64,INVALID_BASE64_DATA!!!";
}
```

**Backend Impact:**

```python
frame_data = frame_data.split(",")[1]  # "INVALID_BASE64_DATA!!!"

image_bytes = base64.b64decode(frame_data)
# Raises: binascii.Error: Incorrect padding

# Exception caught
await websocket.send_json({
    "success": False,
    "error": "No frame data received"  # Misleading error message
})
```

---

### Breakpoint 6: Memory Exhaustion

**Problem:**

```python
# Multiple frames accumulating in memory
heatmap_frames = []  # Never cleared

for frame in stream:
    heatmap = generate_heatmap(...)
    heatmap_frames.append(heatmap)  # Growing list
    # After 1000 frames: ~3.6 GB memory used ❌
```

**Result:**

```
MemoryError or system slowdown after ~10 minutes
```

---

## 🎨 FRONTEND STATE UPDATES

### State Update Flow After WebSocket Message

```javascript
ws.onmessage = (event) => {
  // 1. Parse
  const data = JSON.parse(event.data);
  console.log("📨 Received:", data);

  // 2. Validate
  if (!data.success) {
    console.error("Backend error:", data.error);
    setError(data.error);
    return;
  }

  // 3. Update Core Metrics
  setCount(Math.round(data.count || 0));
  // State update 1: count
  // Re-render: Status panel updates immediately

  // 4. Update Performance Metrics
  setFps(data.fps || 0);
  // State update 2: fps
  // Re-render: Status panel updates

  setInferenceTime(data.timing?.total_ms || data.timing?.inference_ms || 0);
  // State update 3: inferenceTime
  // Re-render: Status panel updates

  // 5. Store Full Response
  setResults(data);
  // State update 4: results (entire object)
  // Re-render: CSRNetCard displays JSON

  // 6. Extract Heatmap
  if (data.heatmap) {
    console.log("🔥 Setting heatmap, length:", data.heatmap.length);
    setHeatmapImage(data.heatmap);
    // State update 5: heatmapImage
    // Re-render: <img> tag src updated
    // Browser decodes base64 and displays image
  } else {
    console.log("⚠️ No heatmap in response");
    // heatmapImage stays null
    // No update
  }

  // 7. Extract Density Stats
  if (data.density_map_stats) {
    setDensityStats(data.density_map_stats);
    // State update 6: densityStats
    // Re-render: Stats card updates
  }

  // 8. Update Status Message
  setStatus(
    `Processing - Count: ${Math.round(data.count || 0)} | ` +
      `FPS: ${data.fps?.toFixed(1) || 0} | ` +
      `Inference: ${data.timing?.inference_ms?.toFixed(0) || 0}ms`
  );
  // State update 7: status (combined string)
  // Re-render: Status panel text updates

  // 9. Clear Error (if any)
  setError(null);
  // State update 8: error cleared
};
```

### Component Re-render Cascade

```
WebSocket receives JSON
    ↓
ws.onmessage triggered
    ↓
setCount(45)  ← State update 1
    ↓
Webcam.js function component re-runs
    ↓
Render section:
    ├─ <StatusPanel>
    │  ├─ count prop = 45  ← New value
    │  ├─ fps prop = 7.95
    │  ├─ status prop = "Processing - Count: 45..."
    │  └─ Re-renders with new text
    │
    └─ <HeatmapCard>
       ├─ heatmapImage prop = "data:image/jpeg;base64,..."
       ├─ <img src={heatmapImage} />  ← New src
       └─ Browser loads new image
            └─ Image decoder processes base64
            └─ JPEG decompressed
            └─ Blitted to screen
            └─ User sees heatmap ✅

    └─ <CSRNetCard>
       ├─ results prop = {count: 45, fps: 7.95, ...}
       └─ <pre>{JSON.stringify(results)}</pre>
            └─ Pretty-prints JSON
            └─ User sees raw data ✅

Total re-render time: ~50-100ms
Visible update latency: ~5-10ms after message arrival
```

---

## 📊 DATA SIZE SUMMARY TABLE

| Stage  | Component      | Format       | Size    | Notes               |
| ------ | -------------- | ------------ | ------- | ------------------- |
| **1**  | Webcam         | Raw stream   | N/A     | Continuous          |
| **2**  | Canvas         | RGBA buffer  | 1.2 MB  | In memory only      |
| **3**  | JPEG           | Encoded      | 92 KB   | 80% quality         |
| **4**  | Base64         | String       | 123 KB  | +33% overhead       |
| **5**  | WebSocket      | Binary frame | 123 KB  | Network             |
| **6**  | Backend        | JSON         | 123 KB  | Parsed              |
| **7**  | Frame          | JPEG bytes   | 92 KB   | Decompressed        |
| **8**  | PIL Image      | Object       | 50 KB   | Lazy-loaded         |
| **9**  | Tensor         | GPU/CPU      | 921 KB  | float32             |
| **10** | Density Map    | Tensor       | 19 KB   | (60x80)             |
| **11** | Heatmap BGR    | Array        | 3.6 MB  | (480x640x3)         |
| **12** | Heatmap JPEG   | Bytes        | 98.5 KB | Encoded             |
| **13** | Heatmap Base64 | String       | 131 KB  | +33% overhead       |
| **14** | Response       | JSON         | 131 KB  | Complete            |
| **15** | Frontend       | String       | 131 KB  | In JS memory        |
| **16** | Browser        | Image        | ~5 MB   | Decoded for display |

---

**Report Generated:** November 25, 2025  
**Version:** Complete Data Flow Documentation
