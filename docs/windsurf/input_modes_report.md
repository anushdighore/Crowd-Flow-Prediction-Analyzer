# Input Modes Report

This report summarizes the major **input modes** supported by the system and how they map to backend APIs, models, and outputs.

Modes covered:

- **Upload Image** (static images)
- **Live Webcam** (local camera)
- **External IP Camera** (network camera streams)
- **Video Upload** (pre-recorded video files)

Issue IDs (W‑xxx) refer to `issues_overview.md`.

---

## Overview Matrix

| Mode            | Transport | Primary Endpoint(s)                      | Models (intended)                               | Key Outputs                                | Status / Notes                               |
| --------------- | --------- | ---------------------------------------- | ----------------------------------------------- | ------------------------------------------ | -------------------------------------------- |
| Upload Image    | REST      | `POST /api/v1/csrnet/count`              | CSRNet                                          | `count`, `raw_count`, timings              | Working                                      |
|                 |           | `POST /api/v1/tmtb/count`                | TMTB / VMamba                                   | `count`, `raw_count`, timings              | Working                                      |
|                 |           | `POST /api/v1/yolo/detect`               | YOLOv8                                          | `count`, `boxes`, `annotated_image`        | Working                                      |
| Live Webcam     | WebSocket | `ws://localhost:8000/ws/count`           | CSRNet, TMTB/VMamba, YOLOv8 (intended)          | `count`, `fps`, heatmap/overlay, tracks    | Mismatched model routing (W‑001,W‑002,W‑003) |
| External Camera | WebSocket | `ws://localhost:8000/ws/external-camera` | CSRNet, TMTB/VMamba, YOLOv8 (+ auto-switch)     | `frame`, `heatmap`, `count`, tracks, stats | Working; heatmap always computed (W‑006)     |
| Video Upload    | WebSocket | `ws://localhost:8000/ws/video-process`   | YOLO variants, CSRNet (limited), MCNN (UI only) | `count`, `fps`, heatmap/overlay, tracks    | MCNN unsupported (W‑005)                     |

---

## Upload Image

### CSRNet

- **Route**: `POST /api/v1/csrnet/count`
- **Handler**: `backend/app/api/v1/endpoints/csrnet.py::count`
- **Request**: multipart form upload with `file: UploadFile` (image).
- **Outputs**:
  - `status`: `"success"` on success.
  - `count`: integer rounded count (`rounded_count`).
  - `raw_count`: float count.
  - `inference_time_ms`, `device`, `original_size`, `processed_size`.
  - Heatmaps are currently **disabled by default** in this endpoint (no `return_heatmap` toggle exposed).

### TMTB / VMamba

- **Route**: `POST /api/v1/tmtb/count`
- **Handler**: `backend/app/api/v1/endpoints/tmtb.py::count`
- **Request**: multipart `file`.
- **Outputs**:
  - Same structure as CSRNet (`count`, `raw_count`, timings, sizes).
  - No heatmap or density map visualization in this REST endpoint; it is treated as numeric-only.

### YOLOv8

- **Routes**:
  - Simple count: `POST /api/v1/yolo/count` (returns bounding boxes and average confidence).
  - Detailed detect: `POST /api/v1/yolo/detect` (adds `annotated_image` in base64 when available).
- **Handler**: `backend/app/api/v1/endpoints/yolo.py`.
- **Request**: multipart `file`.
- **Outputs**:
  - `count`, `raw_count`, `inference_time_ms`, `device`.
  - `boxes` with `x1,y1,x2,y2,confidence`.
  - Optionally `annotated_image` (data URL) for `/detect`.

**Status**: All three image upload endpoints are **coherent and working**; no major mismatches detected for this mode.

---

## Live Webcam

- **Frontend**:

  - Page: `frontend/src/pages/webcam/Webcam.js`.
  - Context: `frontend/src/context/WebcamContext.js`.
  - Right menu: `frontend/src/components/Menu/RightMenu.js`.

- **Backend**:
  - WebSocket handler: `backend/app/main.py::websocket_count` at `/ws/count`.

### Transport and payload

- Transport: **WebSocket**, URL `ws://localhost:8000/ws/count`.
- Payload per frame:

  ```json
  {
    "frame": "data:image/jpeg;base64,...",
    "model": "csrnet" | "vmamba" | "yolov8",
    "tracking": true | false,
    "heatmap": true | false,
    "threshold": 0.1–0.95
  }
  ```

- `frame` is captured from `<video>` into `<canvas>` and encoded via `toDataURL("image/jpeg", 0.8)`.

### Backend behavior

- Uses `model` to decide between **CSRNet**, **TMTB/VMamba**, and **YOLO** branches.
- Uses `heatmap` to decide whether to return a `heatmap` image.
- Uses `tracking` only in YOLO branches to enable `UnifiedCounter` with tracking.
- `threshold` is currently ignored.

### Issues

- **W‑001** – `"vmamba"` and `"yolov8"` values are not recognized by the YOLO/TMTB branches, so webcam always falls back to CSRNet.
- **W‑002** – The YOLO model size setting (`yoloVersion`) is never encoded into the `model` string for this mode.
- **W‑003** – Confidence `threshold` is unused, making the slider cosmetic.

See `webcam_pipeline_report.md` for an in-depth walkthrough.

---

## External IP Camera

- **Frontend**:

  - Page: `frontend/src/pages/ExternalCamera/ExternalCamera.js` (and older `ExternalCameraPage.js`).
  - Utilities: `CameraControls`, `SettingsPanel`, `StreamStats`, etc.
  - Uses `WS_BASE = "ws://localhost:8000"` → `/ws/external-camera`.

- **Backend**:
  - WebSocket handler: `backend/app/main.py::websocket_external_camera` at `/ws/external-camera`.
  - Camera client: `app.camera.camera.camera_client` for frame acquisition.

### Transport and protocol

1. **Configuration message** (sent once when starting the stream):

   ```json
   {
     "camera_url": "http://.../video",
     "model": "csrnet" | "tmtb" | "yolo-nano" | ...,
     "tracking": true | false
   }
   ```

2. **Frame requests** (polled by the frontend every ~200 ms):

   ```json
   { "action": "get_frame" }
   ```

### Backend behavior

- Retrieves frames via `camera_client.get_frame(camera_url)`.
- For YOLO + tracking: uses `UnifiedCounter`.
- Otherwise: delegates to the **GatedModelRouter** `model_router.predict(...)`:
  - Uses `model_type` to pick CSRNet/TMTB/YOLO.
  - Returns density maps or boxes as appropriate.
- Heatmap logic:
  - For YOLO: generates heatmap from boxes (when boxes exist) via `model_router.generate_heatmap`.
  - For CSRNet/TMTB: generates heatmap from density map.
- Response per frame (simplified):

  ```json
  {
    "success": true,
    "frame": "data:image/jpeg;base64,...",   // original frame
    "heatmap": "data:image/jpeg;base64,...", // overlay, if available
    "count": <int>,
    "raw_count": <float>,
    "fps": <float>,
    "frame_number": <int>,
    "unique_count": <int?>,
    "tracks": [...],
    "speed_stats": {...},
    "advanced_metrics": {...}
  }
  ```

### Issues / notes

- **W‑006 (Info)** – There is no `heatmap` flag in the protocol; the backend always attempts heatmap computation even if the UI hides it. Behavior is acceptable for now but important for performance discussions.

---

## Video Upload

- **Frontend**:

  - Component: `frontend/src/components/Models/YOLO/VideoUploader.js`.
  - Uses `ws://localhost:8000/ws/video-process`.

- **Backend**:
  - WebSocket handler: `backend/app/main.py::websocket_video_process` at `/ws/video-process`.

### Transport and protocol

1. **Configuration message** (on WebSocket open):

   ```json
   {
     "model": "yolo-nano" | "yolo-small" | "csrnet" | "mcnn",
     "tracking": true | false,
     "confidence": 0.0–1.0
   }
   ```

2. **Per-frame messages** (sent as the user’s video plays, ~30 FPS):

   ```json
   {
     "frame": "data:image/jpeg;base64,...",
     "timestamp": <seconds>,
     "frame_number": <int>
   }
   ```

3. **Stop message**:

   ```json
   { "action": "close" }
   ```

### Backend behavior

- Maps YOLO variants using a `yolo_model_map` and uses `UnifiedCounter` or `yolo_api` accordingly.
- For `model == "csrnet"`, uses CSRNet prediction; other density models (e.g. MCNN) are not implemented.
- Returns for each frame (simplified):

  ```json
  {
    "success": true,
    "frame_number": <int>,
    "model": "yolo-..." | "csrnet",
    "count": <float>,
    "tracks": [...],
    "unique_count": <int?>,
    "speed_stats": {...},
    "advanced_metrics": {...},
    "heatmap": "data:image/jpeg;base64,..." // when available
  }
  ```

### Issues

- **W‑005** – The UI offers `"mcnn"`, but `websocket_video_process` treats unknown `model_type` as `"Unknown model"` and returns errors.
- Confidence `confidence` is accepted but currently used only in configuration; the exact wiring into YOLO thresholds should be verified as part of follow-up work.

---

## Mode Comparison and Current Priorities

- **Most reliable today**:

  - Upload Image (CSRNet/TMTB/YOLO) – clean REST contracts, no major mismatches.
  - External IP Camera – model routing and tracking are wired correctly; heatmap is always computed.

- **Needs alignment work**:
  - Live Webcam – core of W‑001/W‑002/W‑003.
  - Video Upload – W‑005 (MCNN option) and potential threshold tuning.

`fix_plan.md` breaks down concrete minimal changes per issue and mode.
