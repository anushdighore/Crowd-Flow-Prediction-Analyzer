# 🏗️ System Architecture (Implemented)

The deployed system delivers real-time and batch crowd counting through a React frontend, a FastAPI backend, and a shared inference layer that serves multiple neural models. This document captures the architecture that is live in the repository today—training jobs and dataset preparation are handled separately and are intentionally excluded here.

---

## 🔭 High-Level Overview

- **User Interaction Layer**: CRA-based React app (`frontend/`) with upload and webcam modes plus runtime model selection.
- **API Gateway**: FastAPI service (`backend/app/main.py`) exposing REST endpoints under `/api/v1/*` and a WebSocket at `/ws/count`.
- **Multi-Model Inference Core**: Model adapters in `ml/src/models/` (CSRNet, VMamba/TMTB, YOLOv8, MCNN) with shared preprocessing/postprocessing utilities.
- **Configuration & Resources**: YAML-driven configuration (`backend/config/`, `ml/csrnet_config.yaml`), checkpoint storage (`ml/checkpoints/`, `ml/fine-tunned/`), and runtime caches.
- **Launch & Ops Tooling**: Batch scripts (`start_app.bat`, `backend/start_backend.bat`, `start_multimodel.bat`) and monitoring aids (logging dashboards, TensorBoard for inference diagnostics).

---

## 🧱 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION LAYER                        │
│ ┌──────────────────────────────┐   ┌──────────────────────────────────┐ │
│ │ React Frontend (Port 3000)   │   │ Launch Scripts / CLI Utilities  │ │
│ │ • Upload Mode (HTTP POST)    │   │ • start_app.bat                 │ │
│ │ • Webcam Mode (WebSocket)    │   │ • start_backend.bat             │ │
│ │ • Model Selector UI          │   │ • start_multimodel.bat          │ │
│ └────────────┬─────────────────┘   └────────────────┬─────────────────┘ │
│              │                                     │                   │
└──────────────┼─────────────────────────────────────┼────────────────────┘
                             │ HTTP / WebSocket                    │ Local orchestration
                             ▼                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             API GATEWAY LAYER                           │
│ FastAPI Service (backend/app/main.py)                                   │
│ • REST Routers: /api/v1/csrnet, /api/v1/tmtb                            │
│ • Real-time WebSocket: /ws/count                                        │
│ • Health/metadata endpoints: /health, /api/models, /api/current-model   │
│ • Connection manager & session metrics                                  │
└──────────────┬──────────────────────────────────────────────────────────┘
                             │ delegates
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          MULTI-MODEL INFERENCE CORE                     │
│ ml/src/                                                                │
│ • Model Adapters: models/csrnet, models/tmtb, models/yolov8_counter,    │
│   models/mcnn, models/tmtb/model_factory                               │
│ • Pre/Post Processing: preprocessing/, utils/, shared/                 │
│ • Device Management & Model Caching                                    │
│ • Prediction API consumed by FastAPI                                   │
└──────────────┬──────────────────────────────────────────────────────────┘
                             │ reads configs & checkpoints
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     CONFIGURATION & RESOURCE LAYER                      │
│ • backend/config/*.yaml (API sizing, limits)                            │
│ • ml/csrnet_config.yaml (inference sizing, data handling)               │
│ • ml/checkpoints/, ml/fine-tunned/ (model weights)                      │
│ • shared/ (logging, helpers), backend/target/ (bundled assets)          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 1. User Interaction Layer (React Frontend)

- **Codebase**: `frontend/` (Create React App).
- **Modes**:
  - **Upload Mode** – Sends still images via POST `/api/v1/{model}/count`.
  - **Webcam Mode** – Streams frames over WebSocket `/ws/count` with per-frame metrics.
  - **Model Switcher** – Chooses CSRNet, VMamba-TMTB, YOLOv8, or MCNN at runtime (mirrors backend model factory).
- **State & UX**: Maintains live count overlay, FPS statistics, and connection status.
- **Static Assets**: Built bundles served by CRA dev server (port 3000) or exported build artifacts.

## 2. API Gateway & Real-Time Services (FastAPI)

- **Entry Point**: `backend/app/main.py` (multi-model ready FastAPI application).
- **Routers** (`backend/app/api/v1/endpoints/`):
  - `csrnet.py` – Upload and webcam endpoints with CSRNet-specific preprocessing.
  - `tmtb.py` – Mirror endpoints for VMamba-TMTB model.
- **WebSocket**: `/ws/count` managed by `websocket_count` for low-latency webcam inference.
- **Cross-Origin**: CORS configured for localhost React dev servers.
- **Health & Metadata**:
  - `/` – Service banner and model list.
  - `/health` – Basic health probe.
  - Multi-model service (`predict_multimodel.py`) adds `/api/models`, `/api/current-model`, `/api/select-model` when launched.
- **Operational Concerns**: Structured logging, exception handling, and graceful disconnects.

## 3. Multi-Model Inference Core (`ml/src/`)

- **Model Adapters**:
  - `models/csrnet/api.py` – CSRNet inference adapter using cached PyTorch weights.
  - `models/tmtb/api.py` – VMamba-TMTB adapter with lazy loading and config-driven sizing.
  - `models/yolov8_counter.py` & `models/mcnn.py` – Optional detectors supported by the model factory.
- **Factory & Caching**: `models/tmtb/model_factory.py` centralizes model metadata, checkpoint paths, and device assignment; adapters memoize loaded weights.
- **Preprocessing**: `preprocessing/` & `utils/preprocess.py` resize, normalize, and convert frames to tensors, respecting config dimensions per source (upload/webcam/video).
- **Postprocessing**: `utils/postprocess.py` and model-specific helpers convert density maps or detections into calibrated counts and diagnostics.
- **Device Management**: Automatically selects CUDA when available, falls back to CPU, and synchronizes for accurate timing.

## 4. Configuration & Resource Layer

- **Configuration Loader**: `backend/app/core/config.py` provides cached YAML access with dot-notation lookups.
- **Backend Configs**: `backend/config/config.yaml`, `backend/config/hyperparams.yaml` define API behaviour, image sizing, and runtime limits.
- **ML Inference Configs**: `ml/csrnet_config.yaml` controls CSRNet inference dimensions per source; `ml/config/` stores shared hyperparameters for runtime transforms.
- **Model Assets**: Checkpoints in `ml/checkpoints/` (pretrained) and `ml/fine-tunned/` (project-specific tuned models) are mounted read-only by the backend at startup.
- **Shared Utilities**: `shared/` hosts reusable logging, path, and validation helpers used across backend and ML layers.

## 5. Request Flows (Without Training)

### Upload Image Flow

1. **React Upload** → POST `/api/v1/{model}/count` with multipart image.
2. **Backend Router** validates file, converts to PIL, delegates to model adapter.
3. **Inference Core** resizes using config, runs model, sums density map or detections, returns count + timing.
4. **Frontend** displays rounded count, raw count, and latency metrics.

### Webcam Flow

1. **React Webcam** encodes frames (Base64 JPEG) and streams over WebSocket.
2. **FastAPI WebSocket** decodes frame, chooses selected model, runs inference via adapter.
3. **Inference Core** produces count, FPS, and optional density statistics.
4. **Backend** pushes JSON payload (`count`, `fps`, `timing`) back to UI.

## 6. Operations & Tooling

- **Launchers**: `start_app.bat` (full stack), `backend/start_backend.bat`, `start_multimodel.bat`, plus helper scripts in `scripts/` for cache cleanup and dependency checks.
- **Monitoring**: Console logs, optional TensorBoard for inference diagnostics, and structured log files under `logs/`.
- **Static Artifacts**: Built frontend assets and cached model files stored under `backend/target/` and `ml/checkpoints/` respectively.

---

## 📌 Key Entry Points

| Component            | Path                                 | Purpose                                                                         |
| -------------------- | ------------------------------------ | ------------------------------------------------------------------------------- |
| Frontend Dev Server  | `frontend/` → `npm start`            | React UI for upload/webcam modes and model selector                             |
| REST + WebSocket API | `backend/app/main.py`                | Unified service exposing CSRNet/TMTB endpoints and realtime streaming           |
| Multi-Model Service  | `backend/app/predict_multimodel.py`  | Optional service enabling runtime switching across VMamba, CSRNet, YOLOv8, MCNN |
| Inference Adapters   | `ml/src/models/*/api.py`             | Model entry points consumed by FastAPI                                          |
| Config Loader        | `backend/app/core/config.py`         | Cached YAML configuration access                                                |
| Checkpoints          | `ml/checkpoints/`, `ml/fine-tunned/` | Pretrained and tuned weights used during inference                              |

This architecture enables rapid experimentation with different crowd-counting models while preserving a clean separation between the user experience, API surface, and inference logic. All production inference paths run through the components documented above—training and dataset pipelines live elsewhere in the repository.
