# Data Folder Structure

This folder contains test images and videos for ML model testing.

## Directory Structure

```
data/
├── images/
│   ├── crowd/
│   │   ├── high_density/       # Images with >50 people
│   │   ├── medium_density/     # Images with 10-50 people
│   │   └── low_density/        # Images with <10 people
│   ├── intersection/
│   │   ├── pedestrian_vehicle/ # Mixed traffic scenes
│   │   └── crosswalk/          # Crosswalk scenes
│   └── test_samples/           # Quick test set (5-10 images)
├── videos/
│   ├── crowd/
│   │   ├── indoor/             # Indoor crowd videos
│   │   └── outdoor/            # Outdoor crowd videos
│   ├── intersection/           # Traffic intersection videos
│   └── test_samples/           # Short test clips (5-10 seconds)
└── calibration/
    └── homography_points.json  # Calibration data for world coordinates
```

## Adding Test Data

### Images

1. **High Density Crowd** (`images/crowd/high_density/`)

   - Place images with >50 people
   - Formats: `.jpg`, `.png`
   - Example: `crowd_01.jpg`, `stadium_packed.jpg`

2. **Medium Density** (`images/crowd/medium_density/`)

   - Place images with 10-50 people
   - Use for standard testing

3. **Low Density** (`images/crowd/low_density/`)
   - Place sparse scenes (<10 people)
   - Use for edge case testing

### Videos

1. **Test Samples** (`videos/test_samples/`)

   - Add short clips (5-10 seconds)
   - Formats: `.mp4`, `.avi`
   - Keep file sizes small for quick testing

2. **Full Videos** (`videos/crowd/`)
   - Longer videos for comprehensive testing
   - Indoor vs. outdoor separation

### Calibration Data

For homography transformation (V3 feature):

```json
{
  "video_name.mp4": {
    "points_image": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]],
    "points_world": [[0,0], [2,0], [2,2], [0,2]],
    "description": "4 corners of walkable area in meters"
  }
}
```

## Usage in Tests

Tests will automatically discover data:

```python
# In pytest
@pytest.fixture
def data_dir():
    return Path("data")

def test_image(data_dir):
    image_path = data_dir / "images" / "crowd" / "medium_density" / "crowd_01.jpg"
    # ... test code
```

## Test Data Sources

Recommended public datasets:

- **UCF-QNRF**: High-density crowds
- **ShanghaiTech**: Part A (dense), Part B (sparse)
- **Mall Dataset**: Shopping mall videos
- **PETS 2009**: Pedestrian tracking
- **MOT Challenge**: Multi-object tracking

## Gitignore

Large test data is ignored in `.gitignore`:

```
data/images/
data/videos/
!data/images/README.md
!data/videos/README.md
```

## Minimum Test Set

For quick CI/CD testing, maintain a minimal set:

- 3 images in `test_samples/` (~1 MB each)
- 1 short video in `test_samples/` (~5 MB, 5 seconds)

---

**Note:** Add your own test data here. Tests will skip if data is not found.
