# /webcam Unified Experience – Actionable & Verifiable Proposal

## 1. Scope and Goals

- **Scope**: Redesign and align the `/webcam` experience across frontend and backend while fixing issues **W‑001, W‑002, W‑003** from `docs/windsurf/issues_overview.md`.
- **Primary goal**: Make `/webcam` the flagship, reliable demo that:
  - Streams a **live webcam feed** with correct model routing.
  - Exposes a **model selector** and an **auto model selector toggle**.
  - Shows a **density heatmap** window for CSRNet/TMTB.
  - Shows a **trajectory window** for YOLO.
  - Provides a single **Start System** action that validates backend connectivity and starts streaming.
  - Surfaces **graphs and advanced metrics** (counts, FPS, density stats, tracking stats).

Related documentation:

- `docs/windsurf/webcam_pipeline_report.md`
- `docs/windsurf/issues_overview.md`
- `docs/windsurf/input_modes_report.md`
- `docs/windsurf/models_map.md`
- `docs/windsurf/fix_plan.md`

---

## 2. Target /webcam Experience

From the user requirements, `/webcam` SHALL provide:

1. **Live webcam feed window**

   - Continuous local camera preview.
   - Overlays for crowd count, FPS, and inference time.

2. **Model selector**

   - Choices: `CSRNet`, `VMamba TMTB`, `YOLOv8`.
   - Selection MUST actually change the backend model used for inference.

3. **Auto model selector toggle**

   - `Auto Model` toggle that automatically switches between CSRNet and YOLO.
   - Behavior (aligned with External Camera auto-switch):
     - For **low crowd** (count < threshold): prefer `YOLO` (fast detection + trajectories).
     - For **high crowd** (count ≥ threshold): prefer `CSRNet` (density-robust).

4. **Heatmap window**

   - Dedicated panel for **density heatmaps**.
   - Active when current effective model is **CSRNet** or **TMTB**.
   - Shows CSRNet/TMTB overlays only; YOLO overlays are handled separately.

5. **Trajectory window**

   - Dedicated panel or overlay for **YOLO trajectories**.
   - Active when current effective model is a YOLO variant.
   - Uses `UnifiedCounter` tracking output (tracks, speed_stats, advanced_metrics).

6. **Start System button**

   - Single primary CTA labeled `Start System` (or similar) that:
     - Performs a **backend health check** (simple REST/WS ping).
     - Starts the webcam stream (`getUserMedia`) and connects `/ws/count`.
     - Shows clear status: `Backend offline`, `Connecting`, `Streaming`, `Error`.
   - A matching `Stop System` action SHALL cleanly tear down:
     - WebSocket, capture interval, and media tracks.

7. **Graphs and other data**
   - **Graphs** (time-series):
     - Crowd count over time.
     - FPS over time.
   - **Data panels**:
     - For density models: density map stats (min/max/mean/sum).
     - For YOLO + tracking: unique count, speed_stats, advanced_metrics, sample track table.

---

## 3. Actionable Changes

### 3.1 Backend – Fix core webcam issues (W‑001, W‑002, W‑003)

**Goal**: Make `/ws/count` honor the model selector and confidence slider so that the frontend can rely on it.

#### 3.1.1 Normalize `model` values from webcam payload (W‑001)

- **File**: `backend/app/main.py` – `websocket_count` handler.
- **Action**:
  - After `model_type = data.get("model", "csrnet")`, introduce a normalization step:
    - Map `"vmamba"` → `"tmtb"`.
    - Map `"yolov8"` → a default YOLO variant (e.g. `"yolo-nano"`).
  - Keep existing YOLO/TMTB/CSRNet branching logic unchanged.
- **Outcome**:
  - `VMamba TMTB` selection on `/webcam` runs the **TMTB** branch.
  - `YOLOv8` selection runs the **YOLO** branch.

#### 3.1.2 Wire YOLO variant strings for /webcam (W‑002)

- **Files**:
  - `frontend/src/context/WebcamContext.js` – `captureAndSend`.
  - `frontend/src/components/Menu/RightMenu.js` – YOLO settings (source of `yoloVersion`).
- **Action**:
  - In `captureAndSend`, compute `payload.model` based on `selectedModel` and YOLO size:
    - If `selectedModel === "YOLOv8"` and `settings.yoloVersion === "nano"` → `"yolo-nano"`.
    - Similarly for `small`, `medium`, `large`, `xlarge` → `"yolo-small"`, ...
  - For CSRNet and TMTB, send canonical names `"csrnet"` and `"tmtb"`.
- **Outcome**:
  - `/ws/count` can select correct YOLO checkpoint via its existing `yolo_model_map`.

#### 3.1.3 Use `threshold` to influence YOLO detections (W‑003)

- **File**: `backend/app/main.py` – `websocket_count`.
- **Action**:
  - Read `threshold = data.get("threshold", 0.5)`.
  - Pass `threshold` into YOLO inference:
    - As `conf_threshold` or equivalent for `UnifiedCounter` and/or `yolo_api.predict`.
- **Outcome**:
  - Changing the confidence slider in `/webcam` clearly changes detection density.

---

### 3.2 Frontend – Unified /webcam layout and controls

**Goal**: Implement the target UX features without major architectural changes.

#### 3.2.1 Consolidated /webcam layout

- **Files**:
  - `frontend/src/pages/webcam/Webcam.js`.
  - Supporting components: `HeatmapOverlay`, `TrajectoryCanvas`, `CountDisplay`.
- **Action**:
  - Ensure `/webcam` page layout has three main regions:
    1. **Live feed** (video element) with count/FPS overlay.
    2. **Analysis panels**:
       - Density heatmap card (`HeatmapOverlay` with `modelType` = `csrnet`/`tmtb`).
       - Trajectory canvas (`TrajectoryCanvas`) layered over the video.
    3. **Graphs + stats**:
       - Count/FPS over time (simple line charts or sparkline-like components).
       - Density stats and tracking stats panels.
  - Wire `results` and `densityStats` / `speed_stats` / `advanced_metrics` from `WebcamContext` into these regions.

#### 3.2.2 Model selector and Auto Model toggle

- **File**: `frontend/src/components/Menu/RightMenu.js`.
- **Action**:

  - Ensure the right menu contains:
    - **Model selector**: CSRNet / VMamba TMTB / YOLOv8.
    - **Auto Model toggle** (`autoModelEnabled`):
      - When ON, the manual selector is treated as a _starting_ model; the context may switch model based on logic below.
      - When OFF, model changes only when the user explicitly picks a model.
  - Add an **Auto-switch threshold** slider (reuse semantics from External Camera if desired).

- **File**: `frontend/src/context/WebcamContext.js`.
- **Action**:
  - Add state:
    - `autoModelEnabled`, `autoSwitchThreshold` (e.g. 30), `currentAutoModel`.
  - In `onmessage` handler for `/ws/count`:
    - If `autoModelEnabled` is true and a stable `count` is available:
      - If `count < autoSwitchThreshold` and `currentAutoModel` not YOLO → switch to YOLO variant.
      - If `count ≥ autoSwitchThreshold` and `currentAutoModel` is YOLO → switch to CSRNet.
    - When switching:
      - Update `selectedModel` and `currentAutoModel` in context.
      - Send a small control message or simply let the next `captureAndSend` payload reflect the new `model`.

#### 3.2.3 Heatmap window behavior

- **Files**:
  - `Webcam.js`, `HeatmapOverlay.js`.
- **Action**:
  - Show **density heatmap** panel only when current effective model is `csrnet` or `tmtb`.
  - For YOLO, keep overlays in the video region (as a detection overlay), not in the CSRNet/TMTB heatmap card.
  - Clearly label the heatmap panel as `Density Heatmap (CSRNet/TMTB)`.

#### 3.2.4 Trajectory window behavior

- **Files**:
  - `Webcam.js`, `TrajectoryCanvas.js`, `CountDisplay.js`.
- **Action**:
  - Show `TrajectoryCanvas` only when effective model is YOLO and `tracking` is enabled.
  - Ensure it uses the same track schema as External Camera / Video modes (`tracks`, `state`, `trajectory`, etc.).
  - Display `unique_count`, `speed_stats`, and a small table of active tracks in a side panel.

#### 3.2.5 Start System / Stop System button

- **Files**:
  - `RightMenu.js` (button), `WebcamContext.js` (logic).
- **Action**:
  - Rename/clarify the main button as **Start System** / **Stop System**.
  - On **Start System**:
    - Optionally perform a simple health check:
      - REST: `GET /api/health` or similar (if not present, use a small test connection to `/ws/count`).
    - If backend is reachable, proceed to `handleStartStreaming()`.
    - If not, show a toast: `Backend not reachable on port 8000` and do not start webcam.
  - On **Stop System**:
    - Call `stopEverything()` to clear intervals, close WS, and stop tracks.
    - Confirm UI status as `Stopped`.

---

### 3.3 Frontend – Graphs and data panels

#### 3.3.1 Count and FPS history graphs

- **Files**:
  - `WebcamContext.js` – new arrays `countHistory`, `fpsHistory`.
  - New lightweight chart component (e.g. `WebcamMetricsGraph.js`).
- **Action**:
  - On each successful `/ws/count` message, append: `{ time: Date.now(), count }` and `{ time: Date.now(), fps }` (keeping last N points, e.g. 50).
  - Render simple line/bar graphs for count and FPS over time.

#### 3.3.2 Density and tracking stats panels

- **Files**:
  - Reuse or extend existing stats cards.
- **Action**:
  - For CSRNet/TMTB, show `density_map_stats` (min/max/mean/sum) in a density panel.
  - For YOLO with tracking, show `speed_stats` and a compact `tracks` table, similar to Video mode.

---

## 4. Verifiable Outcomes

This section lists concrete checks to verify the `/webcam` experience behaves as intended.

### 4.1 Model routing and heatmap/trajectory behavior

1. **CSRNet selection**

   - **WHEN** user selects `CSRNet` and `Auto Model` is OFF.
   - **THEN** backend responses have `model: "csrnet"`.
   - **AND** density heatmap panel updates with CSRNet heatmaps.
   - **AND** trajectory window is hidden.

2. **TMTB selection**

   - **WHEN** user selects `VMamba TMTB` and `Auto Model` is OFF.
   - **THEN** backend responses use the TMTB branch (e.g. model string `"tmtb"`).
   - **AND** density heatmap panel updates with TMTB overlays.
   - **AND** trajectory window is hidden.

3. **YOLO selection**

   - **WHEN** user selects `YOLOv8` and `Auto Model` is OFF.
   - **THEN** backend responses indicate a YOLO model (e.g. `"yolo-nano"`, `"yolo-small"`).
   - **AND** responses include `boxes` and (with tracking ON) `tracks`, `unique_count`, `speed_stats`.
   - **AND** trajectory window is shown and updating.
   - **AND** density heatmap panel is hidden.

4. **Heatmap behavior**

   - **WHEN** `heatmap` toggle is ON and a density model is active.
   - **THEN** responses contain `heatmap` and `density_map_stats`, and the density heatmap panel shows an image.

5. **Threshold effect on YOLO**
   - **WHEN** `threshold` is set to 0.1 for YOLO.
   - **THEN** `num_detections` is greater than or equal to the `num_detections` observed at threshold 0.8 on the same scene.

### 4.2 Auto model behavior

1. **Low-crowd → YOLO**

   - **GIVEN** `Auto Model` is ON, `autoSwitchThreshold = 30`.
   - **WHEN** observed count stabilizes below 30.
   - **THEN** effective model becomes YOLO (model string in responses is YOLO variant).

2. **High-crowd → CSRNet**

   - **GIVEN** `Auto Model` is ON, `autoSwitchThreshold = 30`.
   - **WHEN** observed count stabilizes at or above 30.
   - **THEN** effective model becomes CSRNet.

3. **Manual override**
   - **WHEN** `Auto Model` is OFF and user selects a model.
   - **THEN** model does not change automatically based on count.

### 4.3 Start/Stop lifecycle and connectivity

1. **Backend offline**

   - **GIVEN** backend is not running on port 8000.
   - **WHEN** user clicks `Start System`.
   - **THEN** a clear error toast appears and webcam does not start streaming.

2. **Successful start**

   - **GIVEN** backend is running.
   - **WHEN** user clicks `Start System`.
   - **THEN** status changes to `Streaming`, live feed appears, and count/FPS values update.

3. **Clean stop**
   - **WHEN** user clicks `Stop System`.
   - **THEN** video stream is paused, WebSocket is closed, and capture timers are cleared.
   - **AND** no further `/ws/count` messages are processed.

### 4.4 Graphs and stats

1. **Count/FPS graphs**

   - **WHEN** streaming runs for > 10 seconds.
   - **THEN** count and FPS graphs show at least several data points and scroll as new points arrive.

2. **Density stats**

   - **WHEN** CSRNet or TMTB is active with heatmap enabled.
   - **THEN** a density stats panel shows min/max/mean/sum values updating over time.

3. **Tracking stats**
   - **WHEN** YOLO with tracking is active.
   - **THEN** `unique_count`, `speed_stats`, and a track table update as people move.

---

## 5. Issue Mapping

- **W‑001** – Fixed by 3.1.1 and 3.2.x behaviors ensuring `model` names align and branches are reachable.
- **W‑002** – Fixed by 3.1.2 wiring YOLO variant IDs from RightMenu to `/ws/count`.
- **W‑003** – Fixed by 3.1.3 introducing real threshold handling in YOLO inference.
- Other issues (W‑004..W‑006) remain documented and are out of strict `/webcam` scope but are captured in `docs/windsurf/fix_plan.md`.
