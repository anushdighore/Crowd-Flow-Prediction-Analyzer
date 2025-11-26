# /webcam Remediation Proposal

## Context Recap (docs/final3)

- `issue-register.md` identifies blockers ISSUES 001-008; ISSUE-001/002/003 directly impact `/webcam` connectivity, heatmap delivery, and latency telemetry.
- `project-context.md` confirms `/webcam` is the canonical live feed combining CSRNet/TMTB/YOLO outputs within a single dashboard.
- `input-flow-report.md` highlights three broken widgets on `/webcam`: heatmap overlays, inference timing, and toast feedback when the WebSocket fails.

## Feature Targets (per user brief)

1. Live webcam feed window that mirrors the active stream from the browser camera.
2. Model selector (CSRNet | TMTB | YOLO) + auto model selector toggle.
3. Heatmap window that renders whenever CSRNet or TMTB is active and the backend signals `return_heatmap`.
4. Trajectory window that activates only when YOLO is selected (leveraging UnifiedCounter output).
5. "Start System" button that boots the backend session (WS connect + local getUserMedia) and shows the live feed plus the correct visualization (density heatmap for CSRNet/TMTB, trajectories for YOLO).
6. Graphs and metrics cards (counts, inference latency, FPS, unique trajectories, etc.).
7. Ancillary data (status toasts/logs, backend health indicator, config summary) so operators know which model/port is in use.

## Actionable Plan

1. **Stabilize Connectivity & Launch Flow (ISSUE-001 + Start Button)**

   - Introduce a shared `envConfig` utility inside `frontend/src/config/` to derive `http(s)` + `ws(s)` base URLs from environment variables; refactor `WebcamContext`, `RightMenu`, and any `/webcam` helpers to use it.
   - Update the "Start System" button to execute: `ensureBackendAlive()` (REST ping), `startBackendSession()` (open WebSocket), and `startCameraStream()` (getUserMedia + canvas loop). Provide disabled/loading states while any step is pending.
   - Ensure the button is visible/primary on `/webcam` even when the sidebar is collapsed; expose `Stop System` for cleanup.

2. **Model Selection & Auto Mode Governance (ISSUE-004 alignment)**

   - Build a dedicated `WebcamControlPanel` component housing: model dropdown, auto-model toggle, heatmap toggle, tracking toggle, and start/stop button. Wire it to `WebcamContext` actions instead of routing everything through `RightMenu`.
   - Persist selection in context + `localStorage` so refreshes keep the operator’s preference. When auto-mode is enabled, show which backend model is currently chosen.

3. **Heatmap Pipeline Fix (ISSUE-002)**

   - Backend: move CSRNet/TMTB density heatmap encoding outside the YOLO branch in `backend/app/main.py` so every density response includes `heatmap` when requested.
   - Frontend: unify heatmap payload parsing and ensure the Heatmap window only displays for CSRNet/TMTB (or future density models). Provide a placeholder message when YOLO is active, linking to the trajectory window instead.

4. **Trajectory Window & YOLO Telemetry**

   - Extend the WebSocket payload contract so YOLO responses include trajectory polylines + unique counts in a dedicated key (documented in a TS/JS type file). Guard-render the `TrajectoryVisualizer` component only when YOLO is selected.
   - Surface tracker status badges (e.g., "Tracking Live" / "Tracker Offline") fed by backend telemetry so operators know when data is stale.

5. **Metrics, Graphs, and Other Data (ISSUE-003 & ISSUE-008)**

   - Fix latency/FPS cards by reading `data.inference_time_ms` (with backwards-compatible fallback) and computing rolling averages.
   - Add mini-charts (counts over last N frames) using existing Chart.js setup; feed them via `useMemo` to minimize renders.
   - Replace the unused Bootstrap toast dependency with a lightweight React notification hook so connection errors/success states are visible without external assets.
   - Display backend health/state (WS connected, backend host/port, dropped frames) inside a compact status panel.

6. **Regression Shielding**
   - Snapshot-test `WebcamControlPanel` state permutations and integration-test the WebSocket handler via mocked payloads (CSRNet heatmap + YOLO trajectories) so regressions in the feed windows are caught automatically.
   - Document the `/webcam` flow in `docs/final3/input-flow-report.md` once fixes land (who owns what, toggles, fallback behavior).

## Verifiable Outcomes

1. **Connectivity Verification**

   - QA script: start backend on a non-localhost host:port, set `REACT_APP_API_BASE_URL`, run `/webcam`, and confirm WS connects over the derived URL. Capture screenshots/logs.
   - Automated test: React Testing Library test ensures `Start System` triggers `getUserMedia` mock + `connectWebSocket` promise chain.

2. **Model Selector & Auto Toggle**

   - Manual test matrix covering manual CSRNet/TMTB/YOLO picks plus auto mode switching (simulate backend-suggested model). Acceptance criteria: UI updates active model label within 1s; toggle state persists across reload.

3. **Heatmap Window**

   - Integration test feeding mocked CSRNet payload with `heatmap` ensures `<HeatmapWindow>` renders image and hides trajectory section. For TMTB, same behavior.
   - QA: When YOLO active, heatmap window displays informational state, not stale image.

4. **Trajectory Window**

   - Unit test verifying YOLO payload renders polylines and updates unique count card. Negative test ensures CSRNet/TMTB payload leaves trajectory window dormant.

5. **Metrics & Notifications**

   - Jest test confirming `inference_time_ms` drives latency card. Cypress (or manual) test verifying notifications show on WS error, without Bootstrap dependency warnings.

6. **Documentation Update**
   - After implementation, append a "Post-remediation status" section to `docs/final3/input-flow-report.md` referencing resolved issue IDs and linking to commits. Reviewers can verify documentation changes in PR diff.
