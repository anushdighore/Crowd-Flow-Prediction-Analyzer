# New Features in Version 3

## Table of Contents

1. [Advanced Tracking System](#advanced-tracking-system)
2. [Pedestrian Dynamics Analysis (PedPy)](#pedestrian-dynamics-analysis)
3. [Intersection Analysis](#intersection-analysis)
4. [World Coordinate Mapping](#world-coordinate-mapping)
5. [PyQt6 Desktop Application](#pyqt6-desktop-application)
6. [Multi-Object Tracking](#multi-object-tracking)

---

## Advanced Tracking System

### Kalman Filter Tracking

**File:** `v3Updates/tracker_ped.py`, `v3Updates/CrowdAnalyzer.py`

V3 introduces sophisticated tracking using Kalman filters for motion prediction and Hungarian algorithm for data association.

```python
class Track:
    def __init__(self, box, track_id):
        self.id = track_id
        self.state = TrackState.NEW  # NEW → TRACKED → LOST
        self.kf = KalmanFilter(dim_x=4, dim_z=2)  # x, y, vx, vy

        # State transition matrix
        self.kf.F = np.array([
            [1, 0, 1, 0],   # x = x + vx*dt
            [0, 1, 0, 1],   # y = y + vy*dt
            [0, 0, 1, 0],   # vx = vx
            [0, 0, 0, 1]    # vy = vy
        ])
```

**Benefits:**

- ✅ Persistent track IDs across frames
- ✅ Handles occlusions and temporary disappearances
- ✅ Smooth trajectory prediction
- ✅ Reduced ID switches

### Track State Management

```python
class TrackState:
    NEW = 0        # Just detected, not confirmed
    TRACKED = 1    # Confirmed and actively tracked
    LOST = 2       # Lost for too long, removed
```

**Logic:**

- New detections start as `NEW`
- After 3 consecutive hits → `TRACKED`
- If missed for 10 frames → `LOST` (removed)

### Hungarian Matching

Optimal assignment of detections to existing tracks:

```python
def _hungarian_match(self, cost_matrix):
    """
    Match detections to tracks using Hungarian algorithm
    Cost = Euclidean distance between detection and predicted position
    """
    row_idx, col_idx = linear_sum_assignment(cost_matrix)

    matched = []
    for r, c in zip(row_idx, col_idx):
        if cost_matrix[r, c] < 30.0:  # Distance threshold
            matched.append((r, c))

    return matched, unmatched_dets, unmatched_tracks
```

---

## Pedestrian Dynamics Analysis

### PedPy Integration

**Library:** `pedpy` - Pedestrian dynamics analysis  
**File:** `v3Updates/CrowdAnalyzer.py`

V3 integrates PedPy for comprehensive pedestrian behavior analysis.

### 1. Density Estimation

Three different methods:

#### Classic Density

```python
classic_density = compute_classic_density(
    traj_data=traj,
    measurement_area=measurement_area
)
# Density = count / area
```

#### Voronoi Density

```python
individual_voronoi = compute_individual_voronoi_polygons(
    traj_data=traj,
    walkable_area=walkable_area
)
density_voronoi = compute_voronoi_density(
    individual_voronoi_data=individual_voronoi,
    measurement_area=measurement_area
)
```

#### Voronoi with Cutoff

```python
voronoi_cutoff = compute_individual_voronoi_polygons(
    traj_data=traj,
    walkable_area=walkable_area,
    cut_off=Cutoff(radius=12.0)
)
```

### 2. Speed Analysis

Multiple speed calculation methods:

```python
# Classic mean speed
individual_speed = compute_individual_speed(
    traj_data=traj,
    frame_step=25,
    compute_velocity=True,
    speed_calculation=SpeedCalculation.BORDER_SINGLE_SIDED
)
mean_speed = compute_mean_speed_per_frame(
    traj_data=traj,
    measurement_area=measurement_area,
    individual_speed=individual_speed
)

# Directional speed (e.g., downward movement)
speed_direction = compute_individual_speed(
    traj_data=traj,
    frame_step=5,
    movement_direction=np.array([0, -1]),  # Downward
    compute_velocity=True
)

# Voronoi-based speed
voronoi_speed = compute_voronoi_speed(
    traj_data=traj,
    individual_voronoi_intersection=intersecting,
    individual_speed=individual_speed,
    measurement_area=measurement_area
)
```

### 3. Trajectory Storage

**Format:** CSV with world coordinates

```csv
id,frame,x,y
1,0,0.5,0.3
1,1,0.52,0.35
2,0,1.2,0.8
2,1,1.25,0.85
```

**Structure:**

```python
def save_trajectories(self, output_path='trajectories.csv'):
    trajectory_data = []
    for person_id, positions in self.track_history.items():
        for frame_idx, pos in enumerate(positions):
            trajectory_data.append({
                'id': person_id,
                'frame': frame_idx,
                'x': pos[0],  # World x (meters)
                'y': pos[1]   # World y (meters)
            })
    pd.DataFrame(trajectory_data).to_csv(output_path)
```

---

## World Coordinate Mapping

### Homography Transformation

V3 converts image coordinates to real-world coordinates using perspective transformation.

```python
def set_homography_matrix(self, points_image, points_world):
    """
    Calculate homography from 4+ point correspondences

    Args:
        points_image: [(x1,y1), (x2,y2), ...] in pixels
        points_world: [(x1,y1), (x2,y2), ...] in meters
    """
    points_image = np.float32(points_image)
    points_world = np.float32(points_world)
    self.homography_matrix, _ = cv2.findHomography(
        points_image,
        points_world
    )
```

### Interactive Point Selection

```python
class PointSelector:
    """
    GUI for selecting calibration points
    User clicks 4 corners, enters distances in meters
    """
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append([x, y])
            # Draw point and line
            cv2.circle(self.image, (x, y), 5, (0, 255, 0), -1)
```

### Coordinate Transformation

```python
def transform_point(self, point):
    """Transform image pixel → world meters"""
    if self.homography_matrix is None:
        return point

    point_homo = np.array([point[0], point[1], 1.0])
    transformed = self.homography_matrix @ point_homo
    transformed = transformed / transformed[2]  # Normalize

    return (float(transformed[0]), float(transformed[1]))
```

**Use Cases:**

- Real speed in m/s (not pixels/frame)
- Actual density in persons/m²
- Real distances for proximity analysis

---

## Intersection Analysis

### Multi-Class Tracking

**File:** `v3Updates/tracker_pedv.py`

Tracks pedestrians AND vehicles simultaneously.

```python
class IntersectionAnalyzer:
    def __init__(self, model_path='yolov11x.pt'):
        self.class_names = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck"
        }
        self.vehicle_classes = [1, 2, 3, 5, 7]
        self.pedestrian_classes = [0]

        self.unique_persons = set()
        self.unique_vehicles = set()
```

### Zone Management

Define areas of interest:

```python
self.zones = {
    "crosswalk_north": [(x1,y1), (x2,y2), (x3,y3), (x4,y4)],
    "crosswalk_south": [...],
    "lane_1": [...],
}

# Track which objects are in which zones
self.objects_in_zones = defaultdict(
    lambda: {'pedestrians': set(), 'vehicles': set()}
)
```

### Proximity Detection

```python
self.proximity_threshold = 3.0  # meters

def detect_interactions(self, frame_number):
    """Detect pedestrian-vehicle proximity events"""
    for ped_id in self.unique_persons:
        for veh_id in self.unique_vehicles:
            distance = self.calculate_distance(ped_id, veh_id)
            if distance < self.proximity_threshold:
                self.interactions.append({
                    'frame': frame_number,
                    'pedestrian': ped_id,
                    'vehicle': veh_id,
                    'distance': distance
                })
```

---

## PyQt6 Desktop Application

### GUI Features

**File:** `v3Updates/CrowdAnalyzer.py`

Full-featured desktop app with:

1. **Video Loading**

   ```python
   self.load_button = QPushButton("Load Video", self)
   self.load_button.clicked.connect(self.load_video)
   ```

2. **Settings Dialog**

   - YOLO model selection (yolo11x, yolo11l, yolo11m, yolo11s, yolo11n)
   - Tracker selection (ByteTrack, BoT-SORT)
   - Confidence/IoU thresholds
   - PedPy parameters (walkable area, measurement area)
   - Frame rate and sampling

3. **Real-time Processing**

   ```python
   self.timer = QTimer(self)
   self.timer.timeout.connect(self.update_frame)
   self.timer.start(30)  # Process at ~33 FPS
   ```

4. **Plot Visualization**
   - Density plots (3 methods comparison)
   - Speed plots (4 methods comparison)
   - Trajectory visualization
   - AI-generated interpretations (via Groq API)

### AI-Powered Insights

```python
def generate_interpretation(self, image_path, text_widget, plot_type):
    """Use Groq LLM to interpret plots"""
    base64_image = self.encode_image(image_path)
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
            ]
        }]
    )
    # Display markdown interpretation
    text_widget.setHtml(markdown.markdown(response.content))
```

---

## Multi-Object Tracking

### Enhanced YOLO Models

V3 uses **YOLO11** (latest) instead of YOLOv8:

```python
self.model = YOLO('yolo11x.pt')  # Largest, most accurate
# Options: yolo11n, yolo11s, yolo11m, yolo11l, yolo11x
```

### Tracking Algorithms

Two state-of-the-art trackers:

#### ByteTrack

```python
results = self.model.track(
    frame,
    persist=True,
    tracker="bytetrack.yaml",
    conf=0.3,
    iou=0.5
)
```

- ✅ Fast, efficient
- ✅ Good for crowded scenes
- ✅ Handles occlusions well

#### BoT-SORT

```python
results = self.model.track(
    frame,
    persist=True,
    tracker="botsort.yaml",
    conf=0.3,
    iou=0.5
)
```

- ✅ More accurate
- ✅ Better appearance features
- ✅ Slower but more robust

### Track Recovery

Enhanced tracking with recovery mechanisms:

```python
self.max_track_age = 120  # Keep track for 120 frames
self.recovery_iou_threshold = 0.3
self.recovery_distance_threshold = 100

def recover_lost_tracks(self, new_detection):
    """Try to match new detection to recently lost track"""
    for lost_track in self.lost_tracks:
        if self.iou(new_detection, lost_track.last_box) > self.recovery_iou_threshold:
            # Reactivate track
            lost_track.state = TrackState.TRACKED
            return lost_track.id
```

---

## Key Improvements Summary

| Feature           | V2           | V3                           | Benefit          |
| ----------------- | ------------ | ---------------------------- | ---------------- |
| **Tracking**      | None         | Kalman + Hungarian           | Persistent IDs   |
| **Coordinates**   | Image pixels | World meters                 | Real metrics     |
| **Objects**       | Persons only | Persons + 5 vehicle types    | Traffic analysis |
| **Analytics**     | Count        | Density, speed, trajectories | Rich insights    |
| **Models**        | YOLOv8n      | YOLO11x + ByteTrack/BoT-SORT | Better accuracy  |
| **Visualization** | Basic boxes  | Trajectories, zones, plots   | Better UX        |
| **Interface**     | Web only     | Web + Desktop (PyQt6)        | Flexibility      |
| **AI Insights**   | None         | LLM plot interpretation      | Auto-analysis    |

---

**Next:** See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for integration steps
