# Issues Overview

This document summarizes cross-cutting issues affecting the **Live Webcam**, **External Camera**, and **Video Upload** pipelines. Each issue has a stable ID used by other reports (e.g. `webcam_pipeline_report.md`, `fix_plan.md`).

---

## Summary Table

| ID    | Title                                                           | Severity | Area                       | Status   |
| ----- | --------------------------------------------------------------- | -------- | -------------------------- | -------- |
| W-001 | Webcam `model` values do not match backend expectations         | Critical | Webcam `/ws/count`         | Open     |
| W-002 | YOLO version setting not wired into webcam backend model choice | Major    | Webcam `/ws/count` + UI    | Open     |
| W-003 | Webcam `threshold` flag unused by backend                       | Minor    | Webcam `/ws/count`         | Open     |
| W-004 | Dual `/ws/count` implementations with different contracts       | Minor    | Backend apps & docs        | Open     |
| W-005 | Video `MCNN` option unsupported in `/ws/video-process`          | Major    | Video `/ws/video-process`  | Open     |
| W-006 | External camera heatmap compute not gated by UI toggle          | Info     | `/ws/external-camera` + UI | Accepted |

Severity is relative to **end-user correctness and observability** in the current phase (streaming demos and reports), not long-term architecture.

---

## W-001 – Webcam `model` values do not match backend expectations (Critical)

- **Area**

  - Frontend: `WebcamContext.captureAndSend` (payload `model`).
  - Backend: `app.main.websocket_count` (`/ws/count`).

- **Observed**

  - Frontend sends:
    - `"csrnet"` when CSRNet is selected.
    - `"vmamba"` when VMamba/TMTB is selected.
    - `"yolov8"` when YOLOv8 is selected.
  - Backend logic recognizes only:
    - `"tmtb"` for VMamba/TMTB.
    - `"yolo"`, `"yolo-nano"`, `"yolo-small"`, `"yolo-medium"`, `"yolo-large"`, `"yolo-xlarge"` for YOLO variants.
  - Any other `model` value (including `"vmamba"` and `"yolov8"`) falls through to the **CSRNet** branch.

- **Expected**

  - When the user selects **VMamba TMTB**, the backend should route frames to the TMTB API.
  - When the user selects **YOLOv8**, the backend should route frames to a YOLO variant, respecting tracking and heatmap flags.

- **Root cause**

  - Frontend and backend use different **canonical strings** for the same conceptual models, and there is no normalization layer:
    - UI label: `VMamba TMTB` → WebSocket: `"vmamba"` → backend expects `"tmtb"`.
    - UI label: `YOLOv8` → WebSocket: `"yolov8"` → backend expects one of `"yolo-*"`.

- **Impact**

  - Live Webcam **always executes CSRNet** regardless of VMamba/YOLO selections.
  - Tracking and YOLO-specific fields (`boxes`, `unique_count`, `speed_stats`, `advanced_metrics`) are never populated for webcam.
  - Heatmap behavior always follows the CSRNet density-map path, even when the UI says "YOLO".

- **Minimal fix (backend-focused option)**

  - Treat `"vmamba"` as an alias for `"tmtb"` in `/ws/count`.
  - Treat `"yolov8"` as an alias for a YOLO variant (e.g. `"yolo-nano"`).
  - This requires only small modifications in `websocket_count`:
    - Normalize `model_type` before the existing YOLO / TMTB checks.

- **Alternative fix (frontend + backend alignment)**

  - Introduce a shared mapping in `WebcamContext` that converts UI model selections into **canonical backend names** (`"csrnet"`, `"tmtb"`, `"yolo-nano"`, ...).
  - Optionally tighten backend to expect only canonical names and log on unknown models.

- **Status**
  - Open. Fix proposals are documented in `fix_plan.md`.

---

## W-002 – YOLO version setting not wired into webcam backend model choice (Major)

- **Area**

  - Frontend: `RightMenu` YOLO settings (`settings.yoloVersion`).
  - Frontend: `WebcamContext.captureAndSend` payload.
  - Backend: YOLO variant map in `websocket_count`.

- **Observed**

  - RightMenu exposes a `yoloVersion` setting (`"nano"`, `"small"`, `"medium"`, `"large"`, `"xlarge"`).
  - `captureAndSend` **does not use** this field when constructing the payload, and always sends `model: selectedModel.toLowerCase()`.
  - Even after resolving W-001, if `model` is fixed only to a single YOLO value, the backend will always load the same checkpoint.

- **Expected**

  - Changing the YOLO version in the UI should select the corresponding checkpoint path on the backend via the `model` value (`"yolo-nano"`, `"yolo-small"`, etc.).

- **Root cause**

  - The video and external-camera flows encode model size in the `model` string (e.g. `"yolo-nano"`), but the webcam flow does not.

- **Impact**

  - Users cannot truly control the YOLO model size for webcam; the setting is cosmetic.
  - Performance and accuracy tuning for webcam YOLO is blocked until this is wired.

- **Minimal fix**

  - In `captureAndSend`, build `payload.model` from `selectedModel` **and** `settings.yoloVersion`, e.g.:
    - `selectedModel === "YOLOv8"` + `settings.yoloVersion === "nano"` → `"yolo-nano"`.
  - No backend change is required beyond W-001 if `yolo_model_map` already supports these values (it does).

- **Status**
  - Open, but dependent on W-001.

---

## W-003 – Webcam `threshold` flag unused by backend (Minor)

- **Area**

  - Frontend: `RightMenu` (YOLO confidence slider).
  - Frontend: `WebcamContext.captureAndSend` (`threshold` in payload).
  - Backend: `websocket_count` ignores `threshold`.

- **Observed**

  - Payloads include `"threshold": <float>`.
  - The backend never reads or forwards this value to `yolo_api` or `UnifiedCounter`.

- **Expected**

  - Adjusting the “Confidence” slider in the UI should meaningfully change YOLO detection thresholds on the backend.

- **Root cause**

  - The threshold control was added only on the frontend; there is no corresponding parameter in the WebSocket handler.

- **Impact**

  - UX inconsistency: users expect fewer/more detections when adjusting the slider, but behavior does not change.
  - For now this is mostly a **cosmetic / UX** issue because YOLO itself still works.

- **Minimal fix options**

  - **Option A:** Wire `threshold` into the YOLO configuration in `websocket_count` (e.g. pass into `UnifiedCounter` or `yolo_api.predict`).
  - **Option B:** Remove `threshold` from the webcam payload and UI until backend wiring is ready, to avoid confusion.

- **Status**
  - Open. `fix_plan.md` assumes Option A as the long-term outcome.

---

## W-004 – Dual `/ws/count` implementations with different contracts (Minor)

- **Area**

  - `backend/app/main.py` → `@app.websocket("/ws/count")` (current live server via `backend/run.py`).
  - `backend/app/predict_multimodel.py` → separate FastAPI app with its own `/ws/count`.

- **Observed**

  - Both files define a `/ws/count` WebSocket endpoint, but **only `main.py` is wired into the default run script** (`run.py` imports `app.main:app`).
  - The multi-model server in `predict_multimodel.py` uses a slightly different contract:
    - Different `model` values and mapping.
    - Different handling of density vs YOLO heatmaps.

- **Expected**

  - There should be a single, well-documented contract for `/ws/count` in production.
  - Alternative implementations should either live under different paths or be clearly labeled as legacy.

- **Root cause**

  - Evolution of the project from a TMTB-centric multi-model server to the current unified FastAPI app without fully retiring the older entrypoint.

- **Impact**

  - Documentation confusion (some older docs may still refer to the older `/ws/count`).
  - Risk of starting the wrong server locally if someone runs `predict_multimodel.py` directly.

- **Minimal fix**

  - Treat `predict_multimodel.py` as **archived / legacy** in docs.
  - Ensure all new docs and examples always use `run.py` → `app.main:app` as the canonical server.
  - Optionally move `predict_multimodel.py` under `docs/archive` or rename its endpoint.

- **Status**
  - Open (documentation-only). Addressed primarily via the windsor docs.

---

## W-005 – Video `MCNN` option unsupported in `/ws/video-process` (Major)

- **Area**

  - Frontend: `VideoUploader` (`frontend/src/components/Models/YOLO/VideoUploader.js`).
  - Backend: `websocket_video_process` in `app.main`.

- **Observed**

  - `VideoUploader` offers model choices: `"yolo-nano"`, `"yolo-small"`, `"csrnet"`, `"mcnn"`.
  - Backend `websocket_video_process`:
    - Supports YOLO variants named in `yolo_model_map`.
    - Has a simple CSRNet branch.
    - Treats any other `model_type` (including `"mcnn"`) as `"Unknown model"` and returns an error.

- **Expected**

  - Either:
    - MCNN is fully wired on the backend for video, **or**
    - MCNN is hidden/disabled in the UI for video mode until it is supported.

- **Root cause**

  - The MCNN option was added for parity with other modes, but no implementation exists in the `/ws/video-process` handler.

- **Impact**

  - Selecting MCNN in the video UI leads to backend errors / unusable behavior.
  - Confusing for users evaluating model choices in the demo.

- **Minimal fix options**

  - **Option A:** Remove or gray out `"mcnn"` in the `VideoUploader` model list.
  - **Option B:** Add a proper MCNN inference branch in `websocket_video_process`, similar to CSRNet/TMTB density handling.

- **Status**
  - Open. `fix_plan.md` currently recommends Option A as a quick corrective step.

---

## W-006 – External camera heatmap compute not gated by UI toggle (Info)

- **Area**

  - Frontend: `ExternalCameraPage` state `enableHeatmap`.
  - Backend: `/ws/external-camera` handler in `app.main`.

- **Observed**

  - The external camera UI has an `enableHeatmap` boolean that controls **whether the heatmap image is displayed**.
  - Backend **always attempts to compute a heatmap** when possible:
    - For YOLO, from detection boxes (via `model_router.generate_heatmap` or `UnifiedCounter` annotated frames).
    - For CSRNet/TMTB, from density maps.
  - There is no `heatmap` flag in the external camera WebSocket protocol.

- **Expected**

  - Two reasonable behaviors exist:
    - (A) Heatmap is always computed, UI flag only controls rendering.
    - (B) Heatmap computation is gated behind a client flag to save backend compute.
  - The current implementation follows (A).

- **Root cause**

  - Design choice: backend optimized for demonstration and analytics, not yet for fine-grained compute savings.

- **Impact**

  - No correctness issues.
  - Slightly higher compute cost even when heatmap is hidden in the UI.

- **Minimal fix (if needed)**

  - Extend the external camera protocol with a `heatmap` boolean mirroring the webcam flow and gate heatmap generation in the backend.
  - For now this is **informational** and captured here for clarity.

- **Status**
  - Accepted as current behavior; no urgent change required.
