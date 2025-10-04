# 🎨 System Architecture Diagrams

## 1. Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 Web Browser (Chrome/Edge)                  │  │
│  │                    http://localhost:3000                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    React App
                         │
        ┌────────────────┴────────────────┐
        │                                  │
   Upload Mode                        Webcam Mode
        │                                  │
   HTTP POST                          WebSocket
   /count                            /ws/count
        │                                  │
        └────────────────┬────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                     BACKEND LAYER                                │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │  fastapi_app.py  │              │  webcam_app.py   │        │
│  │  (HTTP Server)   │              │  (WebSocket)     │        │
│  └────────┬─────────┘              └────────┬─────────┘        │
│           │                                  │                   │
│           └──────────────┬───────────────────┘                   │
│                          │                                       │
│              ┌───────────▼──────────┐                           │
│              │   Preprocessing      │                           │
│              │  (utils/preprocess)  │                           │
│              └───────────┬──────────┘                           │
│                          │                                       │
│              ┌───────────▼──────────┐                           │
│              │   VMamba-TMTB Model  │                           │
│              │   (Deep Learning)    │                           │
│              │   GPU/CPU Inference  │                           │
│              └───────────┬──────────┘                           │
│                          │                                       │
│              ┌───────────▼──────────┐                           │
│              │   Postprocessing     │                           │
│              │ (utils/postprocess)  │                           │
│              └───────────┬──────────┘                           │
│                          │                                       │
│                   Crowd Count + Metrics                          │
└──────────────────────────┴──────────────────────────────────────┘
```

---

## 2. Webcam Mode Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      STEP 1: Capture                         │
│  Browser → getUserMedia() → Webcam Feed                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 2: Convert                           │
│  Video Element → Canvas → JPEG → Base64                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 3: Send                              │
│  WebSocket.send({ frame: "data:image/jpeg;base64,..." })   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 4: Decode                            │
│  Backend: Base64 → Binary → PIL Image                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  STEP 5: Preprocess                          │
│  Normalize → Tensor [1, 3, H, W] → GPU/CPU                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  STEP 6: Inference                           │
│  Model(tensor) → Density Map [1, 1, H/8, W/8]              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 STEP 7: Count                                │
│  Sum(Density Map) → Calibrate → Count                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 8: Return                            │
│  WebSocket.send({ count: 42, fps: 8.5, timing: {...} })    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 9: Display                           │
│  Update UI: Count Overlay + Metrics Panel                   │
└─────────────────────────────────────────────────────────────┘
```

**⏱️ Total Time: ~100ms (GPU) or ~400ms (CPU)**

---

## 3. Component Interaction Diagram

```
┌────────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                          │
│  ┌──────────────┐                  ┌──────────────┐       │
│  │    App.js    │                  │   Upload     │       │
│  │              │◄─────────────────┤   Component  │       │
│  │  Mode Switch │                  └──────────────┘       │
│  │              │                                           │
│  │              │                  ┌──────────────┐       │
│  │              │◄─────────────────┤   Webcam     │       │
│  └──────────────┘                  │   Component  │       │
│                                     └──────┬───────┘       │
│                                            │                │
└────────────────────────────────────────────┼───────────────┘
                                             │
                                    WebSocket/HTTP
                                             │
┌────────────────────────────────────────────┼───────────────┐
│                   BACKEND (Python)         │               │
│                                            │               │
│  ┌──────────────┐       ┌─────────────────▼─────┐        │
│  │              │       │  Connection Manager    │        │
│  │  Model Loader│       │  (WebSocket/HTTP)      │        │
│  │              │       └─────────────┬──────────┘        │
│  └──────┬───────┘                     │                    │
│         │                             │                    │
│         │         ┌───────────────────▼─────────┐         │
│         │         │  Request Handler            │         │
│         │         │  - Parse frame              │         │
│         │         │  - Validate input           │         │
│         │         └───────────┬─────────────────┘         │
│         │                     │                            │
│         │         ┌───────────▼─────────┐                 │
│         └────────►│  Preprocessing      │                 │
│                   │  - Normalize        │                 │
│                   │  - Resize           │                 │
│                   │  - To Tensor        │                 │
│                   └───────────┬─────────┘                 │
│                               │                            │
│                   ┌───────────▼─────────┐                 │
│                   │  Model Inference    │                 │
│                   │  - Forward pass     │                 │
│                   │  - Density map      │                 │
│                   └───────────┬─────────┘                 │
│                               │                            │
│                   ┌───────────▼─────────┐                 │
│                   │  Postprocessing     │                 │
│                   │  - Sum density      │                 │
│                   │  - Calibrate        │                 │
│                   │  - Extract count    │                 │
│                   └───────────┬─────────┘                 │
│                               │                            │
│                   ┌───────────▼─────────┐                 │
│                   │  Response Builder   │                 │
│                   │  - Format JSON      │                 │
│                   │  - Add metrics      │                 │
│                   └───────────┬─────────┘                 │
│                               │                            │
└───────────────────────────────┼────────────────────────────┘
                                │
                          Send Response
                                │
                                ▼
                          Update UI
```

---

## 4. File Structure Tree

```
Major Project/
│
├── 🚀 LAUNCHERS
│   ├── start_webcam_app.bat         ← Start webcam mode
│   ├── start_upload_app.bat         ← Start upload mode
│   └── GET_STARTED.md               ← You are here!
│
├── 🐍 BACKEND
│   ├── webcam_app.py                ← WebSocket server
│   ├── fastapi_app.py               ← HTTP server
│   ├── test_webcam.py               ← Test suite
│   └── check_dependencies.py        ← Dependency checker
│
├── 🧠 MODELS
│   ├── models/
│   │   ├── vmamba_official.py       ← Model loader
│   │   └── official/
│   │       ├── model.py             ← VMamba architecture
│   │       ├── vmamba.py            ← Core model
│   │       └── counting_head.py     ← Output layer
│   │
│   └── checkpoints/
│       └── jhu_5.pth                ← Trained weights (100-200MB)
│
├── 🛠️ UTILITIES
│   └── utils/
│       ├── preprocess.py            ← Image preprocessing
│       ├── postprocess.py           ← Count extraction
│       ├── webcam.py                ← Webcam utilities
│       └── visualize.py             ← Visualization
│
├── 🌐 FRONTEND
│   └── crowd-counter-frontend/
│       ├── public/                  ← Static assets
│       ├── src/
│       │   ├── App.js               ← Main app + mode switcher
│       │   ├── App.css              ← Main styles
│       │   ├── WebcamCounter.js     ← Webcam component
│       │   ├── WebcamCounter.css    ← Webcam styles
│       │   └── index.js             ← Entry point
│       ├── package.json             ← Dependencies
│       └── node_modules/            ← Installed packages
│
└── 📖 DOCUMENTATION
    ├── GET_STARTED.md               ← Quick start (this file)
    ├── QUICKSTART.md                ← 30-second guide
    ├── WEBCAM_README.md             ← Complete documentation
    ├── PROJECT_SUMMARY.md           ← Technical overview
    └── SYSTEM_DIAGRAMS.md           ← Architecture diagrams
```

---

## 5. WebSocket Communication Protocol

```
CLIENT (React)                          SERVER (FastAPI)

      │                                        │
      │  1. Connect                            │
      ├───────────────────────────────────────►│
      │                                        │
      │                      2. Accept         │
      │◄───────────────────────────────────────┤
      │                                        │
      │  3. Send Frame                         │
      │  {                                     │
      │    "frame": "data:image/jpeg;base64,   │
      │              /9j/4AAQSkZJRg..."       │
      │  }                                     │
      ├───────────────────────────────────────►│
      │                                        │
      │                      4. Process        │
      │                      (100-500ms)       │
      │                                        │
      │                      5. Send Result    │
      │  {                                     │
      │    "success": true,                    │
      │    "count": 42,                        │
      │    "fps": 8.5,                         │
      │    "frame_number": 150,                │
      │    "timing": {                         │
      │      "preprocess_ms": 5.2,             │
      │      "inference_ms": 85.3,             │
      │      "postprocess_ms": 2.1,            │
      │      "total_ms": 92.6                  │
      │    },                                  │
      │    "reasoning": "...",                 │
      │    "density_map_stats": {...}          │
      │  }                                     │
      │◄───────────────────────────────────────┤
      │                                        │
      │  6. Update UI                          │
      │  (Display count + metrics)             │
      │                                        │
      │  7. Send Next Frame                    │
      │  (Loop every 100ms = 10 FPS)           │
      ├───────────────────────────────────────►│
      │                                        │
      │  ...continues...                       │
      │                                        │
      │  N. Disconnect                         │
      ├───────────────────────────────────────►│
      │                                        │
```

---

## 6. State Machine Diagram

```
┌─────────────────────────────────────────────────────────┐
│              WEBCAM MODE STATE MACHINE                   │
└─────────────────────────────────────────────────────────┘

    [App Loaded]
         │
         ▼
    ┌─────────┐
    │ IDLE    │◄───────────────┐
    └────┬────┘                │
         │                     │
         │ Click "Start"       │ Click "Stop"
         ▼                     │
    ┌─────────┐                │
    │ INIT    │                │
    │ WEBCAM  │                │
    └────┬────┘                │
         │                     │
         │ getUserMedia()      │
         ▼                     │
    ┌─────────┐                │
    │ CONNECT │                │
    │ SOCKET  │                │
    └────┬────┘                │
         │                     │
         │ WebSocket.open      │
         ▼                     │
    ┌─────────┐                │
    │STREAMING│────────────────┘
    │         │
    │  Loop:  │
    │ Capture │
    │ → Send  │
    │ → Wait  │
    │ → Update│
    └─────────┘
```

---

## 7. Performance Flow

```
┌──────────────────────────────────────────────────────────┐
│                    PERFORMANCE BREAKDOWN                  │
└──────────────────────────────────────────────────────────┘

Total Time: ~100ms (GPU) or ~400ms (CPU)

├─ Frontend (15ms)
│  ├─ Capture from video (5ms)
│  ├─ Canvas draw (3ms)
│  ├─ To JPEG (5ms)
│  └─ WebSocket send (2ms)
│
├─ Network (5ms)
│  └─ Latency (depends on localhost)
│
├─ Backend Preprocessing (5-10ms)
│  ├─ Base64 decode (2ms)
│  ├─ PIL conversion (1ms)
│  ├─ Normalize (2ms)
│  └─ To tensor (2ms)
│
├─ Model Inference (50-300ms) ★ MAIN BOTTLENECK
│  ├─ GPU: 50-100ms
│  └─ CPU: 200-500ms
│
├─ Backend Postprocessing (2-5ms)
│  ├─ Sum density map (1ms)
│  ├─ Calibration (1ms)
│  └─ Format response (1ms)
│
├─ Network (5ms)
│  └─ Response latency
│
└─ Frontend Update (5ms)
   ├─ Parse JSON (1ms)
   ├─ Update state (2ms)
   └─ Re-render (2ms)

═══════════════════════════════════════════════════════════
💡 OPTIMIZATION TIPS:
- Use GPU for 3-5x speedup
- Lower resolution for 2x speedup
- Skip frames for higher visual FPS
- Use model quantization for CPU
═══════════════════════════════════════════════════════════
```

---

## 8. Error Handling Flow

```
┌─────────────────────────────────────────────────────────┐
│                    ERROR HANDLING                        │
└─────────────────────────────────────────────────────────┘

 User Action → Error Check → Handle → Display
     │              │           │         │
     ▼              ▼           ▼         ▼

1. Click Start
   └─► Webcam Access?
       ├─► YES: Continue
       └─► NO:  Show "Webcam not accessible"
                Check permissions
                Suggest solutions

2. Capture Frame
   └─► Frame Valid?
       ├─► YES: Continue
       └─► NO:  Log error
                Skip frame
                Continue with next

3. Send Frame
   └─► WebSocket Open?
       ├─► YES: Send
       └─► NO:  Show "Connection lost"
                Offer restart

4. Backend Process
   └─► Processing OK?
       ├─► YES: Return result
       └─► NO:  Return error JSON
                {
                  "success": false,
                  "error": "Processing failed",
                  "count": 0
                }

5. Display Result
   └─► Result Valid?
       ├─► YES: Update UI
       └─► NO:  Log to console
                Keep previous count
```

---

## 9. Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│              CURRENT: LOCAL DEPLOYMENT                   │
└─────────────────────────────────────────────────────────┘

    Your Computer
    ┌───────────────────────────────────┐
    │                                   │
    │  ┌─────────────┐  ┌────────────┐ │
    │  │  Backend    │  │  Frontend  │ │
    │  │  :8000      │  │  :3000     │ │
    │  └─────────────┘  └────────────┘ │
    │         │               │         │
    │         └───────┬───────┘         │
    │                 │                 │
    │         ┌───────▼───────┐         │
    │         │   Browser     │         │
    │         │ localhost:3000│         │
    │         └───────────────┘         │
    │                                   │
    └───────────────────────────────────┘


┌─────────────────────────────────────────────────────────┐
│              FUTURE: CLOUD DEPLOYMENT                    │
└─────────────────────────────────────────────────────────┘

    Cloud Server (AWS/Azure/GCP)
    ┌───────────────────────────────────┐
    │                                   │
    │  ┌─────────────┐  ┌────────────┐ │
    │  │  Backend    │  │  Frontend  │ │
    │  │  (Docker)   │  │  (Static)  │ │
    │  └─────────────┘  └────────────┘ │
    │         │               │         │
    │    Load Balancer                  │
    │         │                         │
    └─────────┼─────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    User 1          User 2
  (Browser)       (Browser)
```

---

**Note:** These diagrams provide a visual understanding of the system.
For detailed implementation, see the respective code files.
