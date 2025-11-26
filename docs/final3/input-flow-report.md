# Input Flow Status Report (Webcam • Image • Video • External Camera)

## 1. Webcam Live Page (`/webcam`)

- **Expected flow:** `WebcamContext` acquires local media stream → frames serialized to JPEG → `ws://<API>/ws/count` → backend routes to selected model → returns counts, heatmaps, tracking data.
- **Current status:**
  - Counts update, but `inference_time_ms` is never read (ISSUE-003), so latency/FPS widgets show `0ms`.
  - Heatmap toggle cannot render CSRNet/TMTB overlays because backend never attaches `heatmap` for density models (ISSUE-002). The UI is stuck in “Waiting for heatmap” despite the backend generating density maps.
  - Toast notifications referenced in `WebcamContext` never appear because Bootstrap assets are missing (ISSUE-008), depriving operators of connection feedback.
- **Action items:** Fix backend heatmap path, update frontend to read `inference_time_ms`, and replace toast mechanism or import Bootstrap.

### Post-remediation snapshot (2025-11-25)

- `frontend/src/config/api.js` centralizes API + WebSocket URLs; `/webcam` now honors env-driven hosts & ports (partial mitigation of ISSUE-001).
- `backend/app/main.py` and `WebcamControlPanel` were updated so CSRNet/TMTB responses always include density heatmaps (ISSUE-002) while YOLO renders the dedicated trajectory window instead.
- A dedicated `WebcamControlPanel` and `WebcamMetricsChart` deliver Start System, model/auto toggles, graphs, and notifications driven by React state—Bootstrap toasts are fully removed (ISSUE-004 / ISSUE-008 context for /webcam).
- New `WebcamTrajectoryPanel` reserves the YOLO-only view for tracks/unique counts, with guardrails when tracking is disabled.
- Metrics history powers a rolling trend chart, and all notification pipes use React state so operators see WS/connectivity events without DOM hacks (ISSUE-003 telemetry follow-up).

## 2. Image Upload Page (`/image`)

- **Expected flow:** Users pick a model card (CSRNet/TMTB/YOLO) and upload static images through the dedicated uploader component, receiving counts + optional density visuals.
- **Current status:**
  - Primary uploaders work because they hit `/api/v1/csrnet/count`, `/api/v1/tmtb/count`, `/api/v1/yolo/detect` directly.
  - The legacy visualization grid (currently hidden) still posts to `/api/v1/predict/image`, an endpoint that does not exist (ISSUE-007). If the hidden section is re-enabled, every request will return 404, causing confusion.
  - Side-menu toggles shown on the page actually manipulate the webcam context due to ISSUE-004, so enabling heatmap/auto-mode there has no effect on image uploads.
- **Action items:** Remove or correct the obsolete `/api/v1/predict/image` calls, and decouple the RightMenu from webcam-only state before reintroducing the visualization grid.

## 3. Video Upload Page (`/video`)

- **Expected flow:** User uploads MP4/AVI → `VideoUploader` spawns a WebSocket session (`/ws/video-process`), streams frames, and displays annotated responses.
- **Current status:**
  - Core upload and streaming loop remains intact; however, the only visible “Start Streaming” control still comes from RightMenu, which calls `handleStartStreaming()` (webcam) instead of the video processor (ISSUE-004). Users must press the custom “Start video processing” button inside `VideoUploader`—the sidebar button is misleading.
  - All HTTP/WS URLs are hard-coded to `localhost:8000` (ISSUE-001), so remote operators cannot process videos unless they tunnel traffic or edit sources.
- **Action items:** Hide or repurpose the global RightMenu button on this page and centralize API URLs.

## 4. External IP Camera Page (`/external-camera`)

- **Expected flow:** User enters RTSP/MJPEG URL → clicks _Start Stream_ → frontend opens `/ws/external-camera`, periodically requests frames, and renders live feed, heatmap, metrics, and tracking data.
- **Current status:**
  - There is no Start/Stop button anymore. The previous `SettingsSidebar`—which wired `startStream()`—was removed, and the RightMenu button only launches the local webcam (ISSUE-004 + ISSUE-005). As a result, the external camera pipeline cannot be started at all.
  - Even if invoked manually, any transient tracking error forces `enable_tracking = False` inside the backend loop (ISSUE-006), so unique counts/trajectories disappear silently.
  - Heatmap toggle is rendered but cannot be changed because the controls live in the deleted sidebar.
  - All API URLs and WebSocket endpoints are hard-coded to `http://localhost:8000`, preventing remote usage (ISSUE-001).
- **Action items:** Reintroduce dedicated controls that call `startStream/stopStream`, maintain tracking intent separately from runtime errors, and move API base URLs into config.

## 5. Cross-cutting Connectivity Observations

- None of the frontend modules read `.env` or runtime config for API locations; everything assumes localhost + HTTP. This blocks cloud or multi-host setups and prevents secure `wss://` upgrades (ISSUE-001).
- The only way to initiate any pipeline today is via the single `RightMenu` component, but that component always manipulates webcam state. Until it is refactored, three out of four input flows remain partially or completely non-functional (ISSUE-004/005).

Use this report alongside `issue-register.md` to prioritize remediation per input channel.
