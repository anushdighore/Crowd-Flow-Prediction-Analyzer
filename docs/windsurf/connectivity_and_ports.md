# Connectivity and Ports

This document captures the current **ports**, **base URLs**, and **CORS** settings used by the system, with a focus on the streaming pipelines.

---

## Backend runtime configuration

- **Run script**: `backend/run.py`

  ```python
  uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
  ```

- **Effective backend HTTP/WS port**: `8000`.

- **Config file**: `backend/config/config.yaml`
  - `api.host: "0.0.0.0"`
  - `api.port: 8000`
  - These values match the run script.

---

## Frontend assumptions

- **HTTP base URLs**

  - Image & camera REST calls generally assume `http://localhost:8000`:
    - `ExternalCameraPage`: `API_BASE = "http://localhost:8000/api"`.
    - Model upload components use `/api/v1/...` under that base.

- **WebSocket base URLs**

  - `WS_BASE = "ws://localhost:8000"` in external camera flows.
  - Explicit URLs in contexts/components:
    - Live Webcam: `ws://localhost:8000/ws/count`.
    - External Camera: `ws://localhost:8000/ws/external-camera`.
    - Video Upload: `ws://localhost:8000/ws/video-process`.

- **Frontend dev ports** (React)
  - Typical: `http://localhost:3000` or `http://localhost:5173`.

All of these are consistent with the backend’s configured port `8000`.

---

## CORS configuration

- **In `backend/app/main.py`**:

  ```python
  origins = [
      "http://localhost:3000",
      "http://127.0.0.1:3000",
      "http://localhost:5173",
      "http://127.0.0.1:5173",
      "http://192.168.1.6:3000",
      "http://192.168.1.6:5173",
  ]
  ```

- Applied via `CORSMiddleware` with:
  - `allow_methods=["*"]`
  - `allow_headers=["*"]`
  - `allow_credentials=True`
  - `expose_headers=["*"]`

This configuration covers both localhost dev and a common LAN IP (`192.168.1.6`) on typical React ports (3000/5173).

---

## Streaming endpoints

For completeness, the main WS and REST endpoints involved in streaming are listed here:

- **WebSockets**

  - Live Webcam: `ws://localhost:8000/ws/count`
  - External Camera: `ws://localhost:8000/ws/external-camera`
  - Video Upload: `ws://localhost:8000/ws/video-process`

- **REST**
  - CSRNet: `POST /api/v1/csrnet/count`, `POST /api/v1/csrnet/webcam`.
  - TMTB: `POST /api/v1/tmtb/count`, `POST /api/v1/tmtb/webcam`.
  - YOLO: `POST /api/v1/yolo/count`, `POST /api/v1/yolo/detect`, `POST /api/v1/yolo/webcam`, `POST /api/v1/yolo/track`.
  - Camera utilities: `/api/camera/...` (test connection, etc.).

All of these are rooted at `http://localhost:8000` and are reachable from the configured CORS origins.

---

## Mismatches and recommendations

- **Ports / base URLs**

  - No mismatches detected between frontend assumptions and backend configuration; all expect port `8000`.

- **CORS**

  - Current CORS list is sufficient for local and typical LAN testing.
  - For deployment, consider externalizing allowed origins into configuration (e.g. environment variables) rather than hard-coding.

- **Operational note**
  - If the backend port is changed from `8000`, the following must be updated in lockstep:
    - `backend/run.py` or equivalent server invocation.
    - Any hard-coded `API_BASE` / `WS_BASE` definitions in the frontend.
    - Any reverse proxy / deployment configuration.

At present, the connectivity and ports configuration is **internally consistent**; the main issues tracked in this project are at the payload/model-contract level (see `issues_overview.md`).
