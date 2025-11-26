# Fix Plan

This plan groups the main streaming issues (W‑001..W‑006 from `issues_overview.md`) into small, incremental fixes. The goal is to:

- Restore **correct model routing** for Live Webcam.
- Make YOLO settings actually influence backend behavior.
- Remove or gate unsupported options (MCNN) to avoid broken UX.
- Clarify/document legacy paths without large refactors.

Phases are ordered by **user impact** and **implementation effort**.

---

## Phase P0 – Critical Webcam Model Routing

### P0.1 – Align webcam `model` values with backend expectations (W‑001)

**Goal**: Selecting CSRNet / VMamba / YOLOv8 in the Live Webcam UI should reliably map to CSRNet / TMTB / YOLO on the backend.

**Minimal backend change (recommended as first step)**

- **File**: `backend/app/main.py` – `websocket_count`.
- **Change**:
  - Right after extracting `model_type` (`model_type = data.get("model", "csrnet")`), normalize to canonical names:
    - Map `"vmamba"` → `"tmtb"`.
    - Map `"yolov8"` → `"yolo-nano"` (or another default YOLO variant).
  - This ensures existing YOLO/TMTB branches are hit without touching the frontend.

**Verification**

- Start backend via `backend/run.py` and frontend normally.
- On `/webcam` page:
  - Select **CSRNet** → verify backend `model` field in responses is `"csrnet"`.
  - Select **VMamba TMTB** → verify backend model field changes to something like `"tmtb"` and NO longer logs CSRNet-only messages.
  - Select **YOLOv8** → verify backend model field indicates YOLO (e.g. `"yolo-nano"`), and YOLO-specific fields such as `boxes` start appearing.

**Follow-up frontend clean-up (optional after backend hotfix)**

- Later, we can centralize mapping in the frontend (P1.1) for clarity and unit testing.

---

## Phase P1 – Webcam YOLO Version & Threshold, MCNN UX

### P1.1 – Wire webcam YOLO size selector into `model` (W‑002)

**Goal**: The YOLO version chosen in `RightMenu` (Nano/Small/Medium/Large/XL) should **select the corresponding checkpoint** on the backend.

**Change (frontend)**

- **File**: `frontend/src/context/WebcamContext.js` – function `captureAndSend`.
- **Change**:
  - Instead of sending `model: selectedModel.toLowerCase()`, compute a canonical YOLO model id when `selectedModel === "YOLOv8"`:
    - Use `settings.yoloVersion` to build `"yolo-nano"`, `"yolo-small"`, `"yolo-medium"`, `"yolo-large"`, or `"yolo-xlarge"`.
  - For non-YOLO models, continue to send `"csrnet"` or `"tmtb"` (after aligning with backend naming from P0).

**Verification**

- With logging enabled on the backend, start webcam, select YOLOv8 and change the YOLO version in RightMenu.
- Confirm that each version change leads to different `checkpoint_path` selection based on `yolo_model_map`.
- Sanity-check inference speed and count differences between Nano and larger variants.

### P1.2 – Use webcam `threshold` to tune YOLO confidence (W‑003)

**Goal**: Confidence slider in RightMenu should have an observable effect on YOLO detections.

**Change (backend – minimal version)**

- **File**: `backend/app/main.py` – `websocket_count`.
- **Change**:
  - Read `threshold = data.get("threshold", 0.5)`.
  - When constructing `UnifiedCounter` or calling `yolo_api.predict`, pass this threshold into the appropriate parameter:
    - For example, if `UnifiedCounter` constructor takes `conf_threshold`, either:
      - (A) Re-create counter when threshold changes (simple but slightly heavier), or
      - (B) Add a method to adjust threshold on the existing counter.
    - For direct `yolo_api.predict` calls, add a `conf_threshold` argument if supported.

**Verification**

- On `/webcam` with YOLO selected:
  - Set threshold low (e.g. 0.1) and observe more detections.
  - Set threshold high (e.g. 0.8) and observe fewer detections.
  - Confirm counts and `num_detections` change monotonically with the slider.

### P1.3 – Remove/disable MCNN in Video UI until backend support exists (W‑005)

**Goal**: Prevent user from selecting a model that the backend cannot serve.

**Change (frontend)**

- **File**: `frontend/src/components/Models/YOLO/VideoUploader.js`.
- **Change**:
  - Remove `"mcnn"` from the `models` list **or** mark it disabled (e.g. `ready: false` and grayed-out styling) with a tooltip “Not yet supported for video”.

**Alternative backend improvement**

- Implement an MCNN branch in `websocket_video_process` that mirrors CSRNet/TMTB density handling. This requires MCNN checkpoints and preprocessing to be fully wired.

**Verification**

- UI: MCNN should no longer be selectable or should clearly appear as disabled.
- Backend: no more `Unknown model` errors when using video mode.

---

## Phase P2 – Documentation & Optional Behavior Tweaks

### P2.1 – Clarify and/or archive legacy `/ws/count` (W‑004)

**Goal**: Avoid confusion about which `/ws/count` contract is live.

**Change (docs + light code comment)**

- Ensure all public docs, quickstarts, and examples reference:
  - `backend/run.py` → `app.main:app` as the canonical application.
  - `/ws/count` semantics from `app.main.websocket_count` only.
- Add an inline comment at the top of `predict_multimodel.py` marking it as **legacy** and pointing to `app.main` for the live API.

**Optional**

- Move `predict_multimodel.py` into a `legacy/` or `archive/` package if it’s no longer needed in active development.

**Verification**

- New team members should be able to discover the correct `/ws/count` contract from docs alone.
- No changes to runtime behavior expected.

### P2.2 – Optional: Add heatmap gating to external camera (W‑006)

**Goal**: Allow disabling heatmap computation for external cameras to save compute when not needed.

**Change (protocol + backend)**

- Extend external camera configuration payload to include `heatmap: bool`.
  - E.g. `{ "camera_url": "...", "model": "yolo-nano", "tracking": true, "heatmap": false }`.
- In `/ws/external-camera`:
  - Read and store `enable_heatmap` flag per connection.
  - Only call `model_router.generate_heatmap` / encode `heatmap_frame` when `enable_heatmap` is true.

**Verification**

- With heatmap disabled:
  - Response should omit `heatmap` field.
  - CPU/GPU utilization should decrease relative to heatmap-enabled runs at similar frame rates.

---

## Phase P3 – Optional Future Enhancements

These are **not required** for current functionality but can improve robustness and clarity:

- **P3.1 – Centralized model registry**

  - Introduce a small shared module (backend-first) that defines canonical model IDs and their properties (type, checkpoint, supported modes).
  - Use this registry both in routers and in WebSocket handlers to avoid string drift.

- **P3.2 – Structured telemetry for streaming**

  - Add standardized logging for model selection, thresholds, and heatmap/ tracking flags for each frame/sample.
  - Simplifies debugging and performance profiling.

- **P3.3 – Strong typing of WebSocket messages**
  - Define Pydantic models for WebSocket messages (even if used informally) to keep payloads consistent across modes.

These can be ticketed separately once the P0/P1 fixes are in place.
