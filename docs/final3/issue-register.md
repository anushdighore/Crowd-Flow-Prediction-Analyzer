# Issue Register – Crowd Flow Prediction Analyzer

| ID        | Area                      | Summary                                                                                                           | Impact                                                                                                                                        |
| --------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| ISSUE-001 | Cross-cutting (frontend)  | All HTTP/WebSocket calls hard-code `http://localhost:8000` / `ws://localhost:8000` across contexts and components | Frontend only works when backend is on the same machine and plain HTTP; breaks remote deployments, HTTPS, Docker, and any custom port mapping |
| ISSUE-002 | Backend → Webcam WS       | CSRNet/TMTB heatmaps never emitted because density-map generation lives inside the YOLO branch                    | Webcam “Enable heatmap” toggle can never render heatmaps for density models, blocking primary KPI visualization                               |
| ISSUE-003 | Frontend → Webcam metrics | `WebcamContext` reads `data.timing.*` even though backend sends `inference_time_ms`; inference latency always 0ms | Dashboard metrics and FPS calculations are misleading, making performance monitoring impossible                                               |
| ISSUE-004 | Frontend layout menus     | `RightMenu` ignores props and is hard-wired to webcam context actions                                             | Image, Video, and External Camera pages cannot start their own pipelines; clicking “Start Streaming” always triggers local webcam capture     |
| ISSUE-005 | External camera page      | `startStream()` is never invoked because SettingsSidebar was removed; no UI element calls it                      | Users cannot start external IP camera streams at all, so the entire input path is dead                                                        |
| ISSUE-006 | External camera tracking  | On server fallback, `enable_tracking` is set to `False` without resetting                                         | Tracking silently disables for the remainder of the session after the first counter hiccup                                                    |
| ISSUE-007 | Image page fallback API   | `handleProcessImage` posts to `/api/v1/predict/image`, an endpoint that does not exist                            | Any future attempt to re-enable the legacy panel will immediately 404, causing confusion                                                      |
| ISSUE-008 | Frontend notifications    | Code expects `window.bootstrap.Toast`, but Bootstrap JS/CSS is never imported                                     | Toast notifications for errors/status never appear, reducing user feedback                                                                    |

---

## Detailed Findings

### ISSUE-001 – Hard-coded backend hosts

- **Files:** `src/context/WebcamContext.js` (lines 70-73), `src/components/Models/YOLO/VideoUploader.js` (line 90), `src/components/Models/CSRNet/CSRNetUploader.js` (line 6), `src/pages/ExternalCamera/ExternalCamera.js` (lines 14-16), `src/components/Camera/HLSStreamingPage.js` (lines 12-44), `src/components/Trajectory/PedestrianTracker.js` (line 135), and others.
- **Problem:** Every HTTP and WS call directly points to `http://localhost:8000` / `ws://localhost:8000`. There is no central config, no support for envs, and no `wss://` handling.
- **Impact:** Deployments behind reverse proxies, HTTPS, or different ports instantly fail. Even running the frontend from another machine (e.g., `192.168.x.x`) makes the browser attempt to reach its own localhost instead of the server. Browsers will also block `ws://` when the UI is served over HTTPS.
- **Recommendation:** Introduce a config helper (e.g., `process.env.REACT_APP_API_BASE_URL`) and derive `ws` protocol from `window.location`. Replace hard-coded strings with the helper everywhere.
- **Update (2025-11-25):** `/webcam` now consumes `frontend/src/config/api.js`, so its WebSocket traffic honors env-driven hosts. Remaining pages still need to adopt the helper.

### ISSUE-002 – Heatmap generation unreachable for CSRNet/TMTB

- **File:** `backend/app/main.py`, `websocket_count` handler (~lines 210-270).
- **Problem:** The code that converts `density_map` into a base64 heatmap sits inside the `if model_type in yolo_model_map` block while also checking `model_type not in yolo_model_map`. This condition can never become true.
- **Impact:** Webcam sessions running CSRNet or TMTB never send `heatmap` back, so the frontend’s `HeatmapCard` shows “Waiting for heatmap” indefinitely. This directly breaks the requirement to visualize density maps live.
- **Recommendation:** Move the density-map heatmap logic outside the YOLO branch (or add a separate `elif` for density models) so CSRNet/TMTB results attach `response["heatmap"]` whenever `return_heatmap` is true.
- **Update (2025-11-25):** `backend/app/main.py` now requests density maps from TMTB when `return_heatmap` is true and uses `model_router.generate_heatmap(...)`, ensuring CSRNet/TMTB webcam sessions deliver base64 overlays.

### ISSUE-003 – Wrong field for inference timing

- **File:** `frontend/src/context/WebcamContext.js` (lines 112-121).
- **Problem:** The WebSocket handler uses `data.timing?.total_ms` or `data.timing?.inference_ms`. Backend responses set `inference_time_ms` instead.
- **Impact:** The UI always displays `0ms` inference time, and derived FPS/latency cards mislead operators while debugging performance.
- **Recommendation:** Read `data.inference_time_ms` (and keep `timing` as a fallback if the backend adds it later).

### ISSUE-004 – RightMenu coupled to webcam context only

- **File:** `frontend/src/components/Menu/RightMenu.js`.
- **Problem:** Component signature only accepts `{isOpen, onToggle}` but inside it always pulls state/actions from `useWebcam`. Pages such as Image, Video, and External Camera pass their own props (`selectedModel`, `onStart`) but those props are ignored.
- **Impact:** The only “Start Streaming” button shown anywhere in the app invokes `handleStartStreaming()` from the webcam context. When a user is on the External Camera page, that button unexpectedly starts their laptop webcam instead of the external feed. Likewise, toggles such as “Enable Tracking” merely flip the webcam state.
- **Recommendation:** Refactor `RightMenu` to accept callbacks via props (per page), or create per-page sidebars again. Until then, other input paths remain non-functional.

### ISSUE-005 – External camera start action missing

- **File:** `frontend/src/pages/ExternalCamera/ExternalCamera.js`.
- **Problem:** `startStream` and `stopStream` exist but the only UI that used them (`<SettingsSidebar ... onStart={startStream} />`) is now commented out. No other button calls `startStream`.
- **Impact:** Users cannot launch the external IP camera WebSocket at all—the page forever says “Click Start Stream” but no such button is rendered. Combined with ISSUE-004, the entire external camera flow is dead.
- **Recommendation:** Reintroduce a start/stop control within the page (or wire RightMenu to call `startStream`).

### ISSUE-006 – Tracking flag permanently disabled after fallback

- **File:** `backend/app/main.py`, `websocket_external_camera` (~lines 452-470).
- **Problem:** When tracking fails, the handler sets `enable_tracking = False` and never resets it unless the client reconnects and sends another `camera_url` payload.
- **Impact:** If UnifiedCounter fails to initialize even once, all subsequent frames run without tracking although the UI still displays tracking as enabled. Unique counts and trajectories disappear silently.
- **Recommendation:** Keep a separate `use_tracking` flag to track client intent and only disable tracking for the failing frame (or send an error back instead of mutating the session state).

### ISSUE-007 – Legacy image API targets nonexistent endpoint

- **File:** `frontend/src/pages/StaticTests/Image.js` (lines 159 & 369).
- **Problem:** The fallback handler posts to `http://localhost:8000/api/v1/predict/image`, but no backend router exposes that path.
- **Impact:** If the visualization section is re-enabled (as hinted by TODO), every request fails with 404. Developers may waste time believing the backend is down.
- **Recommendation:** Update the endpoint to an existing route (e.g., `/api/v1/csrnet/count`) or remove the dead code to avoid confusion.

### ISSUE-008 – Bootstrap toasts never load

- **Files:** Multiple references to `window.bootstrap.Toast` in `WebcamContext.js`, but `public/index.html` never loads Bootstrap assets.
- **Impact:** Error/success toasts silently fail, so users get no visual feedback when the WebSocket disconnects or fails.
- **Recommendation:** Either import Bootstrap JS/CSS globally or replace toast logic with a React-native notification library.
- **Update (2025-11-25):** `WebcamContext` dropped Bootstrap DOM hacks in favor of a React `notification` state consumed by `Webcam` to show inline alerts; no external assets required.
