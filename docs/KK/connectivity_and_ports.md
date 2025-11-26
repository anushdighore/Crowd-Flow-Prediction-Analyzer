# Connectivity and Ports

- Frontend
  - Dev server: `http://localhost:3000` (`react-scripts`).
  - WebSocket endpoints:
    - `ws://localhost:8000/ws/count` (`frontend/src/context/WebcamContext.js:72`).
    - `ws://localhost:8000/ws/external-camera` (`frontend/src/pages/ExternalCamera/ExternalCamera.js:15`).
    - `ws://localhost:8000/ws/video-process` (YOLO video) (`frontend/src/components/Models/YOLO/VideoUploader.js:90`).

- Backend
  - FastAPI: `0.0.0.0:8000` (`backend/config/config.yaml:85-89`, `backend/run.py:5-6`).
  - CORS origins: `http://localhost:3000`, `http://localhost:5173` (`backend/config/config.yaml:96-97`, `backend/app/main.py:65`).
  - Static HLS: `/streams` mount → `static/hls` dir (`backend/app/main.py:93-95`, `backend/app/camera/config.py:25`).

- Mismatches and fixes
  - None critical after patches.
  - Recommendation: centralize API/WS base URLs via env in frontend to avoid hardcoding.

