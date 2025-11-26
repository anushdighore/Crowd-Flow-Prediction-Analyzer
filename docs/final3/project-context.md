# Crowd Flow Prediction Analyzer – Project Context

## 1. Mission Overview

The system delivers real-time crowd analytics for four input sources (image upload, video upload, webcam, external IP camera) while fusing results from three ML families (CSRNet density regression, VMamba/TMTB, YOLOv8 + tracker). It targets operators who need counts, heatmaps, trajectories, and derived metrics inside a single dashboard.

## 2. High-Level Architecture

| Layer                  | Key Tech                                                                   | Responsibilities                                                                              |
| ---------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Frontend**           | React 19 (CRA), React Router 7, Chart.js, custom contexts                  | Routing, UI composition, initiating uploads/streams, visualizing counts/heatmaps/trajectories |
| **Backend API**        | FastAPI + Uvicorn, Prometheus instrumentation                              | REST + WebSocket services, HLS packaging, camera abstraction, model routing                   |
| **ML Layer**           | PyTorch models inside `ml/src` (CSRNet, TMTB, YOLOv8, UnifiedCounter)      | Inference, density-map generation, multi-model routing, Kalman-based tracking                 |
| **Streaming Services** | Custom HLS packager, `stream_manager`, MJPEG proxies                       | Converts IP camera feeds into HLS playlists and manages cleanup                               |
| **Tooling**            | Scripts in `/scripts`, notebooks in `/scripts/test.ipynb`, docs in `/docs` | Testing cameras, verifying FFmpeg, documentation and runbooks                                 |

## 3. Codebase Layout (key folders)

- `backend/app/main.py`: Single FastAPI entrypoint registering routers, CORS, WebSocket handlers, Prometheus, and static mounts.
- `backend/app/api/v1/endpoints/`: REST resources per model (`csrnet.py`, `tmtb.py`, `yolo.py`, `pedestrian_tracking.py`).
- `backend/app/camera/`: Camera client abstraction, config, MJPEG streaming, HLS endpoints.
- `backend/app/services/`: Shared services (gated model router, stream manager, HLS packager, ML processor, pedestrian tracker).
- `frontend/src/`: CRA app with `pages/` for flows, `components/` for cards/widgets, `context/` for auth/webcam/global state, `styles/` for layout.
- `ml/`: Training/inference assets, configs, checkpoints (referenced dynamically via `sys.path`).
- `docs/`: Extensive reports (architecture, deployment, troubleshooting) plus the new `docs/final3` folder for this audit.

## 4. Supported Input Pipelines

1. **Image Upload (`/image` route)**
   - Model picker chips render `CSRNetUploader`, `VMambaUploader`, `YOLOUploader`, (MCNN placeholder).
   - Uploaders POST multipart data to `/api/v1/csrnet/count`, `/api/v1/tmtb/count`, `/api/v1/yolo/detect` respectively and show cards for counts, timing, optional heatmaps.
2. **Video Upload (`/video` route)**
   - `VideoUploader` opens `ws://.../ws/video-process`, streams JPEG frames extracted from `<video>` to backend, and replays annotated frames/stats.
3. **Webcam Live (`/webcam`)**
   - `WebcamContext` captures local camera frames, sends them every 100ms to `ws://.../ws/count`, and updates cards (`CSRNetCard`, `HeatmapCard`, stats panel).
4. **External IP Camera (`/external-camera`)**
   - Should use WebSocket `/ws/external-camera` with `camera_url` handshake, plus optional auto model switch, tracking overlays, and metrics cards.
5. **HLS Streaming (`/hls`)**
   - `HLSStreamingPage` triggers `/api/camera/hls/start` to spawn FFmpeg packaging and renders the playlist via `HLSPlayer` (hls.js).

## 5. Primary Backend APIs

| Endpoint                  | Type                   | Purpose                                                               |
| ------------------------- | ---------------------- | --------------------------------------------------------------------- |
| `/api/v1/csrnet/count`    | POST (multipart image) | Density-counting for CSRNet with optional density map                 |
| `/api/v1/tmtb/count`      | POST                   | VMamba-based counter with timing breakdowns                           |
| `/api/v1/yolo/detect`     | POST                   | YOLOv8 detection returning boxes + annotated images                   |
| `/ws/count`               | WebSocket              | Webcam real-time inference with multi-model router                    |
| `/ws/external-camera`     | WebSocket              | Pulls remote MJPEG/RTSP frames via `camera_client` and runs inference |
| `/ws/video-process`       | WebSocket              | Accepts frames from file uploads (client-extracted)                   |
| `/ws/pedestrian-track`    | WebSocket              | Returns trajectories and tracking overlays                            |
| `/api/camera/hls/*`       | REST                   | Manage HLS sessions, playlists, status                                |
| `/camera/test-connection` | GET                    | Validates camera URL reachability                                     |

## 6. Cross-Cutting Services

- **GatedModelRouter**: Chooses CSRNet/TMTB/YOLO API modules and optionally generates heatmaps.
- **UnifiedCounter**: YOLO-based tracker (Kalman + DeepSort style) powering `ml_processor` and extended metrics.
- **Stream Manager & HLS Packager**: Track active streams, run cleanup tasks, and expose playlists under `/streams`.
- **WebcamContext** (frontend): Centralizes stateful webcam lifecycle (start/stop, WebSocket, stats) and is shared with `RightMenu`.

## 7. Execution Scripts

- `start_app.bat`: Launches backend (uvicorn) and frontend (CRA) in separate terminals.
- `backend/start_backend.bat`: Loads `.env`, sets `PYTHONPYCACHEPREFIX`, and starts uvicorn on configured host/port.
- `frontend/package.json`: CRA scripts (`npm start`, `build`, `test`).

## 8. Current Challenges (from audit)

- Multi-model UI shares a single side menu, so non-webcam pages lost their dedicated controls.
- Heatmap + tracking requirements rely on tight coordination between `WebcamContext`, backend WebSockets, and ML services; regressions in any layer manifest as blank cards.
- Configuration is split between `.env`, `config/config.yaml`, and hard-coded constants—no single source of truth for hosts, ports, and feature flags.

This document should help new contributors understand how the pieces fit together before diving into the specific issues captured in `issue-register.md` and the connectivity/flow reports.
