# Fix Plan

- Patch: Model mapping and inference time (frontend)
  - Files: `frontend/src/context/WebcamContext.js`.
  - Diff:
    ```diff
    + const toBackendModel = (name, s) => { /* map YOLO version */ };
    - model: selectedModel.toLowerCase(),
    + model: toBackendModel(selectedModel, settings),
    - setInferenceTime(data.timing?.inference_ms || 0);
    + setInferenceTime(data.inference_time_ms || 0);
    ```
  - Verify:
    - Frontend: `npm start` (port 3000).
    - Backend: `python backend/run.py` (port 8000).
    - Browser: `/webcam` → select `YOLOv8`/version, start; see boxes and non-zero inference time.

- Patch: CSRNet/TMTB heatmap in WS (backend)
  - Files: `backend/app/main.py`.
  - Diff:
    ```diff
    + if return_heatmap and "density_map" in result:
    +   heatmap_overlay = csrnet_api.generate_heatmap(result["density_map"], image)
    +   response["heatmap"] = encode_to_base64(heatmap_overlay)
    ```
  - Verify:
    - `/webcam` → select `CSRNet` or `VMamba`, enable heatmap, start; see overlay image.

- Patch: Unify heatmap toggle (frontend)
  - Files: `frontend/src/components/Menu/RightMenu.js`.
  - Diff:
    ```diff
    - checked={settings.heatmap || false}
    - onChange={(e) => handleSettingChange("heatmap", e.target.checked)}
    + checked={enableHeatmap || false}
    + onChange={(e) => setEnableHeatmap(e.target.checked)}
    ```
  - Verify:
    - Toggle heatmap once; WS payload `heatmap` reflects toggle; UI matches.

- Optional: Reduce logging and configurable FPS
  - Files: `frontend/src/context/WebcamContext.js`.
  - Change: gate logs; add `streamFps` in settings to control interval.

## Manual Test Checklist

- Start servers
  - Backend: `python backend/run.py` → expected: `✅ WebSocket connected for real-time counting` in logs.
  - Frontend: `npm start` → expected: dev server on `http://localhost:3000`.

- Webcam YOLO
  - Navigate `/webcam`.
  - Select `YOLOv8` + `Nano`.
  - Start streaming → expected: boxes visible, `model: yolo-nano`, non-zero `inference_time_ms`.

- Webcam CSRNet
  - Select `CSRNet`, enable heatmap.
  - Start → expected: heatmap overlay rendered, counts update.

- Stop lifecycle
  - Click Stop → expected: WS disconnect toast, counters reset to 0, no further payloads.

