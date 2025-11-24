# v3Updates - Module Summary

This folder (`ml/src/v3Updates`) contains prototype / experimental tracking and analysis scripts used in the VMamba/VMamba-TMTB project. The files are tools for detection, tracking, trajectory export, and PedPy-based density/speed analysis. They are large, self-contained scripts intended for offline video processing and exploratory GUI workflows.

## Files

- `CrowdAnalyzer.py`

  - Purpose: A GUI-driven, full-featured crowd analysis application that integrates YOLO-based tracking, PedPy metrics (density/voronoi/speed), plotting and export features. Provides a PyQt-based user interface for loading a video, selecting calibration points, running detection + tracking, saving processed video, and visualizing density/speed/trajectories.
  - Key classes/functions:
    - `SettingsDialog` — PyQt dialog to configure YOLO/tracker parameters, PedPy settings, frame rate, walkable/measurement areas.
    - `MainWindow` — Main GUI window: load video, start processing, set homography, and run processing loop.
    - `CrowdDensityEstimation` — Core processing class. Wraps YOLO model, does tracking (bytetrack), stores `track_history`, computes PedPy metrics, draws detections and trajectories, transforms coordinates using homography, and saves trajectory CSVs.
    - `PlotWindow` — Shows density/speed/trajectory plots produced by PedPy (uses matplotlib embedded in Qt).
    - Utility classes: `PointSelector`, `Track`, `TrackState`, and plotting/export helper methods.
  - Notable dependencies: `ultralytics.YOLO`, `pedpy`, `filterpy.KalmanFilter`, `scipy`, `PyQt6`, `matplotlib`.
  - Notes / behavior:
    - Uses GPU if available (`torch.cuda.is_available()`), otherwise CPU.
    - Saves processed video and `trajectories.csv` to output folder.
    - Computes classic / voronoi / cutoff density and multiple speed measures via PedPy.
    - Suitable as an end-to-end demo for offline analysis and visualization.

- `tracker_ped.py`

  - Purpose: A compact tracking + trajectory export implementation focused on people (pedestrians). Provides YOLO-based track extraction, simple KalmanFilter-based track management, coordinate transform helpers, and trajectory export.
  - Key classes/functions:
    - `TrackState`, `Track` — Lightweight Kalman-based track object with predict/update/mark_missed.
    - `CrowdDensityEstimation` — Processing class (simpler/leaner than `CrowdAnalyzer.CrowdDensityEstimation`) that wraps a YOLO model, performs `.track()` (bytetrack), draws bounding boxes/IDs, maintains `track_history` (world-coordinates), computes `transform_point` via homography, and saves trajectories to CSV.
    - `PointSelector`, `select_points_and_distances`, `main()` — Support for interactive point selection and sequential world-coordinate entry (used for homography calibration in offline runs).
  - Notable dependencies: `ultralytics.YOLO`, `filterpy.KalmanFilter`, `pandas`, `numpy`, `opencv-python`, `torch`.
  - Notes / behavior:
    - Intended for pedestrian-only scenarios (`classes=[0]`).
    - Uses BYTETRACK tracker via YOLO `track(..., tracker="bytetrack.yaml")`.
    - Offers trajectory smoothing and keeps last N points per track (45 by default).
    - Provides `save_trajectories` which writes a simple CSV of id/frame/x/y.

- `tracker_pedv.py`
  - Purpose: A more advanced intersection / multi-class tracker and interaction analyzer. Tracks pedestrians and vehicles, computes interactions (proximity events), zone membership, and per-class counts; suitable for intersection safety analysis and mixed-traffic scenes.
  - Key classes/functions:
    - `TrackState`, `Track` — Similar Kalman-based track object; tracks may store simple appearance `features` and last box.
    - `IntersectionAnalyzer` — Main class: sets up YOLO (larger model by default), tracks multiple classes (pedestrians + several vehicle classes), maintains `track_history`, computes interactions between pedestrians and vehicles (distance/proximity-based), manages zones (polygons), and draws annotated frames with counts and zones.
    - Methods: `extract_tracks`, `draw_detections`, `process_frame`, `update_trajectories`, `analyze_interactions`, `calculate_direction_and_speed` and many helpers for zone/point-in-polygon calculations.
  - Notable dependencies: `ultralytics.YOLO`, `filterpy.KalmanFilter`, `numpy`, `pandas`, `matplotlib`, `torch`.
  - Notes / behavior:
    - Uses `botsort.yaml` as tracker by default in some calls (or configurable).
    - Computes interactions by proximity threshold and also attempts to compute relative directions; stores interaction events in `self.interactions`.
    - Also supports zone polygons and counting objects per zone.
    - Maintains separate sets for `unique_persons` and `unique_vehicles`.

## Common characteristics and notes

- All scripts use `ultralytics.YOLO` `.track(...)` API and rely on tracker config files (e.g. `bytetrack.yaml`, `botsort.yaml`) being available in the environment where YOLO expects them.
- Kalman-based per-track smoothing is provided via `filterpy.KalmanFilter` in each `Track` class implementation.
- Coordinate transforms / homography: Several scripts expect the user to select 4 image points and provide pairwise real-world distances to derive a simple homography for mapping image pixels → world coordinates. That mapping is used for computing physical densities and speeds (and for drawing world-to-image trajectories).
- Outputs: Typical outputs are processed video (MP4), `trajectories.csv`, density/speed plots (PNG), and interactive Qt windows. `CrowdAnalyzer.py` contains the richest GUI and save/plot functionality.
- Runtime: These scripts are designed for offline processing (load video → process frames). They can use GPU if available; otherwise they run on CPU (much slower).

## How to run (quick)

1. Install required packages (approx):

```bash
pip install -r ml/requirements.txt
# or install core deps
pip install ultralytics opencv-python torch pandas numpy filterpy matplotlib pedpy pyqt6
```

2. Run the GUI analyzer (recommended for exploration):

```bash
python -m ml.src.v3Updates.CrowdAnalyzer
# or
python ml/src/v3Updates/CrowdAnalyzer.py
```

3. For command-line / scripted runs, instantiate and call the processing classes in your own script, e.g.:

```python
from ml.src.v3Updates.tracker_ped import CrowdDensityEstimation
est = CrowdDensityEstimation(model_path='yolo11n.pt')
est.set_homography_matrix(image_points, world_points)
# then for each frame:
processed_frame, info = est.process_frame(frame, frame_number)
```

## Caveats and TODOs

- The code is exploratory and contains debug prints and interactive blocks (mouse callbacks, Qt event loops). Review before integrating into production pipelines.
- Some functions (in `CrowdAnalyzer.py` and the `main()` functions) assume interactive input (QInputDialog or `input()` calls) which require a user to interact during processing.
- There may be minor duplicated logic across `tracker_ped.py` and `tracker_pedv.py` — consider refactoring common track/kalman utilities to a shared module.
- PedPy is used in `CrowdAnalyzer.py` for density/speed computation; ensure `pedpy` is installed when using those features.

## Contact / Next steps

- If you want, I can:
  - Add a top-level test script that runs a single video through `CrowdAnalyzer` headlessly and produces `trajectories.csv` + plots.
  - Extract and refactor shared tracking utilities into `ml/src/v3Updates/_tracking_utils.py` and make each script import from it.
  - Create small unit tests for `transform_point`, `save_trajectories`, and `update_tracks` functions.

---

Generated on: 2025-11-22
