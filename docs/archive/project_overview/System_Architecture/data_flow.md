# 🔄 Data Flow

## 📤 Image Upload Mode (HTTP)

### CSRNet Model Flow:

```
1. User → React UI (CSRNetUploader.js)
   ↓ Select image file

2. React → HTTP POST
   ↓ /api/v1/csrnet/count

3. FastAPI → File validation
   ↓ Size limits, type checking

4. Backend → PIL Image loading
   ↓ Image.open(io.BytesIO(contents))

5. ML Pipeline → CSRNet preprocessing
   ↓ ml/src/models/csrnet/api.py

6. CSRNet Model → Inference
   ↓ Density map generation

7. Postprocessing → Count extraction
   ↓ get_count_from_density()

8. FastAPI → JSON Response
   ↓ {count, raw_count, inference_time_ms, device}

9. React → UI Update
   ↓ Display results with metrics
```

### TMTB/VMamba Model Flow:

```
1. User → React UI (VMambaUploader.js)
   ↓ Select image file

2. React → HTTP POST
   ↓ /api/v1/tmtb/count

3. FastAPI → File validation
   ↓ Size limits, type checking

4. Backend → PIL Image loading
   ↓ Image.open(io.BytesIO(contents))

5. ML Pipeline → TMTB preprocessing
   ↓ ml/src/models/tmtb/api.py

6. TMTB Model → Inference
   ↓ VMamba-TMTB density map

7. Postprocessing → Count extraction
   ↓ Advanced counting logic

8. FastAPI → JSON Response
   ↓ {count, inference_time_ms, device, heatmap_data}

9. React → UI Update
   ↓ Display results with optional heatmap
```

## 🎥 Real-Time Webcam Mode (WebSocket)

### Multi-Model WebSocket Flow:

```
1. User → React WebcamCounter.js
   ↓ Request camera permission

2. Browser → getUserMedia API
   ↓ Access webcam stream

3. React → Canvas capture loop
   ↓ 30 FPS frame capture

4. Canvas → toDataURL('image/jpeg')
   ↓ Base64 JPEG encoding

5. WebSocket → Send frame + model
   ↓ ws://localhost:8000/ws/count
   ↓ {frame: "data:image/jpeg;base64,...", model: "csrnet|tmtb"}

6. FastAPI WebSocket → Receive data
   ↓ main.py websocket handler

7. Backend → Model routing
   ↓ if model == "tmtb": tmtb_api.predict()
   ↓ else: csrnet_api.predict()

8. ML Pipeline → Model-specific preprocessing
   ↓ Config-driven image sizing

9. Selected Model → Real-time inference
   ↓ GPU/CPU processing

10. Postprocessing → Count + metrics
    ↓ {count, inference_time_ms, fps, frame_number}

11. WebSocket → JSON response
    ↓ Real-time updates to frontend

12. React → Live UI updates
    ↓ Count overlay, FPS badge, processing metrics
```

## 🔀 Model Selection Flow

### Dynamic Model Switching:

```
Frontend Selection → API Routing → Model Loading → Inference

1. User clicks model chip (CSRNet/VMamba)
2. React updates selectedModel state
3. Webcam: WebSocket sends model type
4. Upload: HTTP request to model-specific endpoint
5. Backend routes to appropriate model API
6. Model factory loads correct checkpoint
7. Inference uses selected architecture
8. Results formatted per model contract
```

## 📊 Data Processing Details

### Image Preprocessing:

- **CSRNet**: ImageNet normalization, fixed input size
- **TMTB**: Config-driven sizing, advanced preprocessing
- **Webcam**: Real-time frame preprocessing, aspect ratio handling

### Model Inference:

- **CSRNet**: Traditional density regression
- **TMTB**: VMamba state space model with counting head
- **Output**: Density maps → count extraction → metrics

### Response Formatting:

- **Upload**: Detailed JSON with timing, device, sizing info
- **Webcam**: Optimized JSON for real-time updates
- **Error Handling**: Structured error responses with codes

### Performance Optimization:

- **GPU**: CUDA acceleration when available
- **CPU**: Optimized inference for real-time performance
- **Caching**: Model loading optimization
- **Async**: Non-blocking WebSocket communication
