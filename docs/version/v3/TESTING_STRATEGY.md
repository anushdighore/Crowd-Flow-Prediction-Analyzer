# ML Testing Strategy for V3

## Overview

This document outlines the comprehensive testing approach for integrating V3 features into the ML pipeline, focusing on **model-specific tests** with **static images and videos** from the `data/` folder.

## Test Structure

```
ml/tests/
├── csrnet/                 # CSRNet density estimation tests
│   ├── test_static_images.py
│   ├── test_video.py
│   └── test_integration.py
├── yolo/                   # YOLO detection & tracking tests
│   ├── test_detection.py
│   ├── test_tracking.py
│   ├── test_video.py
│   └── yolo_video_test.py (existing)
├── mcnn/                   # MCNN counting tests
│   ├── test_static_images.py
│   └── test_video.py
├── tracking/               # V3 tracking algorithms
│   ├── test_kalman.py
│   ├── test_hungarian.py
│   └── test_track_lifecycle.py
└── integration/            # Full pipeline tests
    ├── test_pedpy_integration.py
    ├── test_homography.py
    └── test_multi_model.py
```

## Data Organization

```
data/
├── images/
│   ├── crowd/
│   │   ├── high_density/      # >50 people
│   │   ├── medium_density/    # 10-50 people
│   │   └── low_density/       # <10 people
│   ├── intersection/
│   │   ├── pedestrian_vehicle/
│   │   └── crosswalk/
│   └── test_samples/          # Small test set
├── videos/
│   ├── crowd/
│   │   ├── indoor/
│   │   └── outdoor/
│   ├── intersection/
│   └── test_samples/          # 5-10 sec clips
└── calibration/
    └── homography_points.json # Calibration data
```

## Test Categories

### 1. Model-Specific Tests

#### CSRNet Tests (`ml/tests/csrnet/`)

**test_static_images.py**

```python
import pytest
from pathlib import Path
from models.csrnet.model import CSRNet

class TestCSRNetImages:
    @pytest.fixture
    def model(self):
        return CSRNet(checkpoint="ml/checkpoints/csrnet.pth")

    @pytest.fixture
    def image_dir(self):
        return Path("data/images/crowd")

    def test_high_density_prediction(self, model, image_dir):
        """Test on crowded scene (>50 people)"""
        image_path = image_dir / "high_density/crowd_01.jpg"
        count, density_map = model.predict(str(image_path))
        assert count > 50, f"Expected >50, got {count}"

    def test_medium_density_prediction(self, model, image_dir):
        """Test on medium crowd (10-50 people)"""
        image_path = image_dir / "medium_density/crowd_02.jpg"
        count, density_map = model.predict(str(image_path))
        assert 10 <= count <= 50

    def test_empty_scene(self, model, image_dir):
        """Test on empty/sparse scene"""
        image_path = image_dir / "low_density/sparse_01.jpg"
        count, density_map = model.predict(str(image_path))
        assert count < 10
```

**test_video.py**

```python
class TestCSRNetVideo:
    def test_video_processing(self, model):
        """Test frame-by-frame video processing"""
        video_path = "data/videos/crowd/outdoor/crowd_video_01.mp4"

        cap = cv2.VideoCapture(video_path)
        frame_counts = []

        for _ in range(30):  # Test first 30 frames
            ret, frame = cap.read()
            if not ret:
                break
            count, _ = model.predict(frame)
            frame_counts.append(count)

        cap.release()

        assert len(frame_counts) == 30
        assert all(c >= 0 for c in frame_counts)
        # Counts should be somewhat stable
        assert np.std(frame_counts) < np.mean(frame_counts) * 0.5
```

#### YOLO Tests (`ml/tests/yolo/`)

**test_detection.py**

```python
from models.yolo.yolov8_counter import YOLOv8Counter

class TestYOLODetection:
    @pytest.fixture
    def detector(self):
        return YOLOv8Counter(
            model_path='yolov8n.pt',
            conf_threshold=0.5
        )

    def test_person_detection(self, detector):
        """Test person detection accuracy"""
        image = "data/images/crowd/medium_density/people_01.jpg"
        count, boxes = detector.predict(image)

        assert count > 0
        assert len(boxes) == count
        # All boxes should be person class (0)
        assert all(box.cls == 0 for box in boxes)
```

**test_tracking.py** ⭐ NEW - V3 Feature

```python
import sys
sys.path.insert(0, 'ml/src/v3Updates')
from tracker_ped import CrowdDensityEstimation

class TestYOLOTracking:
    @pytest.fixture
    def tracker(self):
        return CrowdDensityEstimation(
            model_path='yolo11n.pt',
            conf_threshold=0.3
        )

    def test_track_persistence(self, tracker):
        """Test that tracks persist across frames"""
        video_path = "data/videos/crowd/outdoor/walking_01.mp4"
        cap = cv2.VideoCapture(video_path)

        track_ids_frame1 = set()
        track_ids_frame10 = set()

        for i in range(10):
            ret, frame = cap.read()
            results, _ = tracker.extract_tracks(frame)

            if results[0].boxes.id is not None:
                ids = results[0].boxes.id.cpu().numpy()
                if i == 0:
                    track_ids_frame1 = set(ids)
                elif i == 9:
                    track_ids_frame10 = set(ids)

        cap.release()

        # At least 50% of IDs should persist
        overlap = len(track_ids_frame1 & track_ids_frame10)
        assert overlap >= len(track_ids_frame1) * 0.5
```

**test_video.py**

```python
class TestYOLOVideo:
    def test_full_video_tracking(self, tracker):
        """Test complete video processing with tracking"""
        video_path = "data/videos/crowd/indoor/mall_01.mp4"

        results = process_video_with_tracking(
            video_path,
            tracker,
            max_frames=100
        )

        assert results['frames_processed'] == 100
        assert results['unique_tracks'] > 0
        assert len(results['trajectories']) > 0
```

### 2. V3 Tracking Algorithm Tests (`ml/tests/tracking/`)

**test_kalman.py**

```python
from filterpy.kalman import KalmanFilter
import sys
sys.path.insert(0, 'ml/src/v3Updates')
from tracker_ped import Track

class TestKalmanFilter:
    def test_prediction(self):
        """Test Kalman filter prediction"""
        box = [100, 100, 200, 200]  # x1, y1, x2, y2
        track = Track(box, track_id=1)

        # Predict next position
        predicted = track.predict()

        assert len(predicted) == 2  # x, y
        # Should be near center of box
        assert abs(predicted[0] - 150) < 10
        assert abs(predicted[1] - 150) < 10

    def test_update(self):
        """Test Kalman filter update with measurement"""
        track = Track([100, 100, 200, 200], track_id=1)

        # Update with new measurement
        new_center = np.array([160, 160])
        track.update(new_center)

        assert track.hits == 1
        assert track.time_since_update == 0
```

**test_hungarian.py**

```python
from scipy.optimize import linear_sum_assignment
import sys
sys.path.insert(0, 'ml/src/v3Updates')
from tracker_ped import CrowdDensityEstimation

class TestHungarianMatching:
    def test_optimal_assignment(self):
        """Test Hungarian algorithm for track-detection matching"""
        estimator = CrowdDensityEstimation()

        # Cost matrix: 3 detections x 3 tracks
        cost_matrix = np.array([
            [5, 50, 100],    # Det 0 close to Track 0
            [60, 8, 90],     # Det 1 close to Track 1
            [120, 110, 3]    # Det 2 close to Track 2
        ])

        matched, unmatched_dets, unmatched_tracks = \
            estimator._hungarian_match(cost_matrix)

        # Should match optimally: (0,0), (1,1), (2,2)
        assert len(matched) == 3
        assert (0, 0) in matched
        assert (1, 1) in matched
        assert (2, 2) in matched
```

### 3. PedPy Integration Tests (`ml/tests/integration/`)

**test_pedpy_integration.py**

```python
from pedpy import TrajectoryData, compute_classic_density
import pandas as pd

class TestPedPyIntegration:
    def test_trajectory_loading(self):
        """Test loading trajectories for PedPy"""
        # Load saved trajectories
        df = pd.read_csv("data/test_samples/trajectories_sample.csv")

        traj = TrajectoryData(data=df, frame_rate=30)

        assert len(traj.data) > 0
        assert 'id' in traj.data.columns
        assert 'frame' in traj.data.columns
        assert 'x' in traj.data.columns
        assert 'y' in traj.data.columns

    def test_density_computation(self):
        """Test density calculation"""
        df = pd.read_csv("data/test_samples/trajectories_sample.csv")
        traj = TrajectoryData(data=df, frame_rate=30)

        # Define measurement area
        measurement_area = MeasurementArea([
            (0, 0), (10, 0), (10, 10), (0, 10)
        ])

        density = compute_classic_density(
            traj_data=traj,
            measurement_area=measurement_area
        )

        assert len(density) > 0
        assert all(d >= 0 for d in density)
```

**test_homography.py**

```python
import cv2
import numpy as np
import sys
sys.path.insert(0, 'ml/src/v3Updates')
from tracker_ped import CrowdDensityEstimation

class TestHomographyTransform:
    def test_point_transformation(self):
        """Test image → world coordinate transformation"""
        estimator = CrowdDensityEstimation()

        # Simple square: 100x100 pixels = 2x2 meters
        points_image = [
            [0, 0], [100, 0], [100, 100], [0, 100]
        ]
        points_world = [
            [0, 0], [2, 0], [2, 2], [0, 2]
        ]

        estimator.set_homography_matrix(points_image, points_world)

        # Test center point
        center_img = (50, 50)
        center_world = estimator.transform_point(center_img)

        # Should be close to (1, 1) meters
        assert abs(center_world[0] - 1.0) < 0.1
        assert abs(center_world[1] - 1.0) < 0.1
```

## Test Execution

### Running Tests

```bash
# Run all ML tests
cd ml
pytest tests/ -v

# Run specific model tests
pytest tests/csrnet/ -v
pytest tests/yolo/ -v
pytest tests/mcnn/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run integration tests only
pytest tests/integration/ -v
```

### Test Fixtures

**conftest.py** - Shared fixtures

```python
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def data_dir():
    """Root data directory"""
    return Path("data")

@pytest.fixture(scope="session")
def test_images(data_dir):
    """Test image directory"""
    return data_dir / "images" / "test_samples"

@pytest.fixture(scope="session")
def test_videos(data_dir):
    """Test video directory"""
    return data_dir / "videos" / "test_samples"

@pytest.fixture
def sample_crowd_image(test_images):
    """Single test image"""
    return str(test_images / "crowd_sample.jpg")

@pytest.fixture
def sample_video(test_videos):
    """Single test video"""
    return str(test_videos / "crowd_video_sample.mp4")
```

## Performance Benchmarks

### Target Metrics

| Model    | Metric         | Target    | Test                       |
| -------- | -------------- | --------- | -------------------------- |
| CSRNet   | Inference Time | <100ms    | `test_csrnet_speed()`      |
| CSRNet   | MAE (crowd)    | <10 count | `test_csrnet_accuracy()`   |
| YOLO     | Detection FPS  | >20 fps   | `test_yolo_fps()`          |
| YOLO     | mAP@0.5        | >0.5      | `test_yolo_accuracy()`     |
| Tracking | ID Persistence | >80%      | `test_track_persistence()` |
| PedPy    | Density Calc   | <50ms     | `test_density_speed()`     |

### Benchmark Tests

```python
import time

def test_csrnet_speed(model, sample_crowd_image):
    """Benchmark CSRNet inference speed"""
    times = []
    for _ in range(10):
        start = time.time()
        count, _ = model.predict(sample_crowd_image)
        times.append((time.time() - start) * 1000)

    avg_time = np.mean(times)
    assert avg_time < 100, f"Too slow: {avg_time:.2f}ms"
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: ML Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r ml/requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd ml
          pytest tests/ -v --cov=src
```

## Next Steps

1. ✅ Create test directory structure
2. ⏳ Add sample test data to `data/` folder
3. ⏳ Implement model-specific tests
4. ⏳ Implement V3 tracking tests
5. ⏳ Implement integration tests
6. ⏳ Set up CI/CD pipeline

---

**See Also:**

- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Integration instructions
- [NEXT_ITERATIONS.md](./NEXT_ITERATIONS.md) - Future enhancements
