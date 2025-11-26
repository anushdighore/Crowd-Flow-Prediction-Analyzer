# Issues Overview

- Title: Wrong model mapping for Webcam WS
  - Severity: High
  - Files: `frontend/src/context/WebcamContext.js:314-320`, `frontend/src/components/Menu/RightMenu.js:213-221`
  - Repro:
    - Open `/webcam`, select `YOLOv8` in RightMenu, start streaming.
    - Observe detections behave like density estimation (no boxes).
  - Observed vs Expected:
    - Observed: Backend receives `model: "yolov8"` and defaults to CSRNet.
    - Expected: Backend receives `model: "yolo-nano|small|medium|large|xlarge"` based on YOLO version.
  - Likely Cause: UI uses `YOLOv8` label; client lowers to `yolov8` which backend does not recognize.
  - Minimal Fix:
    - Map UI selection to backend identifiers when sending frames.
    - Diff:
      ```diff
      - model: selectedModel.toLowerCase(),
      + model: toBackendModel(selectedModel, settings),
      ```

- Title: Inference time field mismatch
  - Severity: High
  - Files: `frontend/src/context/WebcamContext.js:107-131`, `backend/app/main.py:280-287`
  - Repro:
    - Start webcam streaming; inference time displays 0 ms.
  - Observed vs Expected:
    - Observed: Client reads `data.timing.*` which is not present.
    - Expected: Use `data.inference_time_ms` returned by backend.
  - Minimal Fix:
    - Read `inference_time_ms` and update status string.
    - Diff:
      ```diff
      - setInferenceTime(data.timing?.inference_ms || 0);
      + setInferenceTime(data.inference_time_ms || 0);
      ```

- Title: CSRNet/TMTB heatmap not generated in WS
  - Severity: High
  - Files: `backend/app/main.py:289-318`
  - Repro:
    - Select `CSRNet` or `VMamba`; enable heatmap; start streaming.
  - Observed vs Expected:
    - Observed: No `heatmap` in WebSocket response.
    - Expected: Density map converted to overlay and returned as `heatmap`.
  - Likely Cause: Heatmap generation block is inside YOLO-specific branch.
  - Minimal Fix:
    - Move density heatmap generation to unified post-processing.
    - Diff:
      ```diff
      + if return_heatmap and "density_map" in result:
      +   heatmap_overlay = csrnet_api.generate_heatmap(result["density_map"], image)
      +   response["heatmap"] = encode_to_base64(heatmap_overlay)
      ```

- Title: Duplicate heatmap toggles cause UX confusion
  - Severity: Medium
  - Files: `frontend/src/components/Menu/RightMenu.js:333-375`, `410-451`
  - Repro:
    - Toggle `🔥 Show Heatmap` in YOLO settings and `🔥 Heatmap` in Display Options.
  - Observed vs Expected:
    - Observed: Two different toggles exist; only `enableHeatmap` affects payload.
    - Expected: Single heatmap toggle drives payload and UI.
  - Minimal Fix:
    - Bind Display Options heatmap to `enableHeatmap` or remove duplicate.
    - Patch:
      ```diff
      - checked={settings.heatmap || false}
      - onChange={(e) => handleSettingChange("heatmap", e.target.checked)}
      + checked={enableHeatmap || false}
      + onChange={(e) => setEnableHeatmap(e.target.checked)}
      ```

- Title: React 19 with `react-scripts` 5 incompatibility risk
  - Severity: Medium
  - Files: `frontend/package.json:16,21`
  - Observed vs Expected:
    - Observed: CRA 5 targets React 18; React 19 may cause HMR/runtime quirks.
    - Expected: Use React 18.x or migrate to Vite.
  - Minimal Fix:
    - Downgrade `react`/`react-dom` to `^18.2.0` or switch to Vite.

- Title: Unused dependency `socket.io-client`
  - Severity: Low
  - Files: `frontend/package.json:22`
  - Observed vs Expected:
    - Observed: No Socket.IO usage in codebase.
    - Expected: Remove unused deps.
  - Minimal Fix:
    - `npm rm socket.io-client` and clean imports if any.

- Title: Verbose logs impact performance
  - Severity: Low
  - Files: `frontend/src/context/WebcamContext.js:97-121`, `backend/app/main.py:275-277`
  - Observed vs Expected:
    - Observed: Frequent console logs per frame.
    - Expected: Debug logs gated or disabled in production.
  - Minimal Fix:
    - Wrap logs behind `process.env.NODE_ENV !== 'production'` or remove.

- Title: Interval rate may saturate CPU on low-end devices
  - Severity: Low
  - Files: `frontend/src/context/WebcamContext.js:356`
  - Observed vs Expected:
    - Observed: 10 FPS capture at quality 0.8.
    - Expected: Adaptive FPS or quality.
  - Minimal Fix:
    - Make FPS configurable; default 6–10 FPS.

