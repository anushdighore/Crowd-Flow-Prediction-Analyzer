# Webcam Pipeline Report

- Start lifecycle:
  - UI: `RightMenu` start → `useWebcam.handleStartStreaming` (`frontend/src/components/Menu/RightMenu.js:124`, `frontend/src/context/WebcamContext.js:329`).
  - Media: `navigator.mediaDevices.getUserMedia` (`frontend/src/context/WebcamContext.js:261`).
  - WS connect: `ws://localhost:8000/ws/count` (`frontend/src/context/WebcamContext.js:72`).
  - Capture: draw to canvas → JPEG base64 (`frontend/src/context/WebcamContext.js:310-314`).
  - Payload: `{ frame, model, tracking, heatmap, threshold }` (`frontend/src/context/WebcamContext.js:314-320`).

- Model selection logic:
  - UI models: `CSRNet`, `VMamba`, `YOLOv8` (`frontend/src/components/Menu/RightMenu.js:213-217`).
  - Mapping: `CSRNet→csrnet`, `VMamba→tmtb`, `YOLOv8 + yoloVersion → yolo-*` (`frontend/src/context/WebcamContext.js:314-320 [patched]`).

- Backend processing:
  - Endpoint: `/ws/count` (`backend/app/main.py:168`).
  - YOLO: maps to checkpoints `yolov8[n|s|m|l|x].pt` (`backend/app/main.py:204-211`).
  - CSRNet/TMTB: density estimation (`backend/app/main.py:266-275`).
  - Response: `success, model, count, inference_time_ms, fps, boxes?, heatmap?` (`backend/app/main.py:280-287`, `289-318 [patched]`).

- Rendering path:
  - Stats: `count`, `fps`, `inference_time_ms` (`frontend/src/context/WebcamContext.js:104-111`, `127-131 [patched]`).
  - Heatmap: base64 overlay image shown via `HeatmapOverlay` (`frontend/src/components/Heatmap/HeatmapOverlay.js:66-78`, `80-105`).
  - Trajectories: when YOLO tracking enabled, `TrajectoryCanvas` draws paths (`frontend/src/components/Trajectory/TrajectoryCanvas.js`).

- Working vs Broken:
  - Working: WS connect/disconnect, count updates, YOLO annotated image when mapping is correct.
  - Broken (fixed): model mapping, inference time field.
  - Broken (backend pre-patch): CSRNet/TMTB heatmap generation inside YOLO block.

```mermaid
flowchart TD
  A[RightMenu Start] --> B[getUserMedia]
  B --> C[connect ws://localhost:8000/ws/count]
  C --> D[capture frame to JPEG base64]
  D --> E[map model to backend ID]
  E --> F[send payload {frame, model, tracking, heatmap}]
  F --> G[FastAPI /ws/count]
  G --> H{Model}
  H -->|YOLO| I[UnifiedCounter/YOLO API]
  H -->|CSRNet/TMTB| J[Density Estimation API]
  I --> K[response: count, inference_time_ms, boxes?, heatmap?]
  J --> L[response: count, inference_time_ms, density_map]
  L --> M[generate heatmap overlay]
  K --> N[WebcamContext onmessage]
  M --> N
  N --> O[HeatmapOverlay / TrajectoryCanvas]
```

