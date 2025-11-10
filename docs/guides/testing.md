# Testing Guide

Complete guide to testing the Multi-Model Crowd Counting System.

## Unit Tests

### Running All Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Running Specific Test File

```bash
# Test models
python -m pytest tests/test_models.py -v

# Test preprocessing
python -m pytest tests/test_preprocessing.py -v

# Test API
python -m pytest tests/test_csrnet_api.py -v

# Test camera integration
python -m pytest tests/test_camera.py -v
```

### Test Coverage Report

```bash
# Generate coverage report
python -m pytest --cov=app --cov-report=html tests/

# View report
open htmlcov/index.html
```

## Integration Tests

### API Endpoint Testing

```bash
# Health check
curl http://localhost:8000/health

# Get server info
curl http://localhost:8000/api/v1/info

# CSRNet prediction
curl -X POST http://localhost:8000/api/v1/csrnet/predict \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'

# VMamba prediction
curl -X POST http://localhost:8000/api/v1/tmtb/predict \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'

# Ensemble prediction
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

### Python Testing Script

```python
# tests/integration_test.py
import requests
import json
import time

API_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_csrnet_prediction():
    payload = {
        "image_url": "https://example.com/image.jpg",
        "visualize": True
    }
    response = requests.post(
        f"{API_URL}/api/v1/csrnet/predict",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] > 0
    print(f"✓ CSRNet prediction: {data['count']} people")

def test_tmtb_prediction():
    payload = {
        "image_url": "https://example.com/image.jpg"
    }
    response = requests.post(
        f"{API_URL}/api/v1/tmtb/predict",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    print(f"✓ VMamba prediction: {data['count']} people")

def test_ensemble_prediction():
    payload = {
        "image_url": "https://example.com/image.jpg"
    }
    response = requests.post(
        f"{API_URL}/api/v1/predict",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "ensemble_count" in data
    print(f"✓ Ensemble prediction: {data['ensemble_count']} people")

if __name__ == "__main__":
    test_health()
    test_csrnet_prediction()
    test_tmtb_prediction()
    test_ensemble_prediction()
    print("\n✓ All tests passed!")

# Run with:
# python tests/integration_test.py
```

## Load Testing

### Using Apache Bench

```bash
# Single request load test
ab -n 100 -c 10 http://localhost:8000/health

# POST request load test
ab -n 50 -c 5 -p payload.json http://localhost:8000/api/v1/csrnet/predict
```

### Using wrk

```bash
# Installation
brew install wrk  # macOS
# Or download from: https://github.com/wg/wrk

# Run load test
wrk -t4 -c100 -d30s http://localhost:8000/health
```

### Using locust

```bash
# Install
pip install locust

# Create locustfile.py
from locust import HttpUser, task, between

class CrowdCountingUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def predict(self):
        self.client.post(
            "/api/v1/csrnet/predict",
            json={"image_url": "https://example.com/image.jpg"}
        )

# Run
locust -f locustfile.py --host http://localhost:8000
```

## Performance Testing

### Latency Measurement

```python
import requests
import time
import statistics

def measure_latency(url, num_requests=10):
    times = []

    for _ in range(num_requests):
        start = time.time()
        response = requests.post(url, json={"image_url": "https://example.com/image.jpg"})
        elapsed = time.time() - start
        times.append(elapsed * 1000)  # Convert to ms

    print(f"Min: {min(times):.2f}ms")
    print(f"Max: {max(times):.2f}ms")
    print(f"Avg: {statistics.mean(times):.2f}ms")
    print(f"Median: {statistics.median(times):.2f}ms")
    print(f"Std Dev: {statistics.stdev(times):.2f}ms")

# Test CSRNet
measure_latency("http://localhost:8000/api/v1/csrnet/predict")

# Test VMamba
measure_latency("http://localhost:8000/api/v1/tmtb/predict")
```

### Memory Profiling

```bash
# Profile memory usage
python -m memory_profiler backend/app/main.py

# Profile with tracemalloc
python -X importtime -u backend/run.py
```

### GPU Utilization Testing

```bash
# Monitor GPU during inference
watch -n 1 nvidia-smi

# Or use nvidia-smi in loop
nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu --format=csv,noheader -l 1
```

## Model Accuracy Testing

### Evaluate on Test Dataset

```python
# ml/src/csrnet/evaluation/evaluate.py
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import mean_absolute_error, mean_squared_error

def evaluate_model(model, test_loader):
    model.eval()
    predictions = []
    ground_truth = []

    with torch.no_grad():
        for images, counts in test_loader:
            output = model(images)
            predictions.extend(output.cpu().numpy())
            ground_truth.extend(counts.cpu().numpy())

    mae = mean_absolute_error(ground_truth, predictions)
    mse = mean_squared_error(ground_truth, predictions)
    rmse = np.sqrt(mse)

    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")

    return {"mae": mae, "rmse": rmse}

# Run evaluation
if __name__ == "__main__":
    model = load_model("weights/csrnet.pth")
    test_loader = DataLoader(test_dataset, batch_size=1)
    results = evaluate_model(model, test_loader)
```

## Automated Testing Pipeline

### GitHub Actions Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", 3.11]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Data

### Generate Test Images

```python
# tests/generate_test_data.py
import numpy as np
from PIL import Image
import cv2

def generate_random_image(width=640, height=480):
    """Generate random test image"""
    img = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    return img

def generate_crowd_image(num_people=50):
    """Generate synthetic crowd image"""
    img = np.ones((480, 640, 3), dtype=np.uint8) * 255

    # Add circles to simulate people
    for _ in range(num_people):
        x = np.random.randint(10, 630)
        y = np.random.randint(10, 470)
        radius = np.random.randint(5, 15)
        cv2.circle(img, (x, y), radius, (0, 0, 255), -1)

    return img

# Generate and save
img = generate_crowd_image(50)
Image.fromarray(img).save("test_crowd.jpg")
```

## Regression Testing

### Before/After Comparison

```python
import json
import requests
from datetime import datetime

def run_regression_test():
    """Test results remain consistent across versions"""

    test_images = [
        "https://example.com/test1.jpg",
        "https://example.com/test2.jpg",
        "https://example.com/test3.jpg"
    ]

    results = {}

    for img in test_images:
        response = requests.post(
            "http://localhost:8000/api/v1/predict",
            json={"image_url": img}
        )
        results[img] = response.json()

    # Save baseline
    with open("tests/baseline_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("✓ Baseline saved")

# Compare with new version
def compare_results():
    with open("tests/baseline_results.json") as f:
        baseline = json.load(f)

    tolerance = 0.1  # Allow 10% variation

    for img, baseline_result in baseline.items():
        response = requests.post(
            "http://localhost:8000/api/v1/predict",
            json={"image_url": img}
        )
        new_result = response.json()

        baseline_count = baseline_result["ensemble_count"]
        new_count = new_result["ensemble_count"]

        diff_percent = abs(new_count - baseline_count) / baseline_count

        if diff_percent > tolerance:
            print(f"✗ {img}: Baseline {baseline_count} → New {new_count}")
        else:
            print(f"✓ {img}: {baseline_count} → {new_count}")
```

## Test Results Documentation

### Example Test Report

```markdown
# Test Results - 2024-01-15

## Unit Tests

- ✓ test_models.py: 12/12 passed
- ✓ test_preprocessing.py: 8/8 passed
- ✓ test_csrnet_api.py: 15/15 passed

## Integration Tests

- ✓ API endpoints responding
- ✓ Model loading successful
- ✓ Predictions consistent

## Performance

- CSRNet latency: 75ms average
- VMamba latency: 40ms average
- Memory usage: 4.2GB
- GPU utilization: 82%

## Accuracy

- CSRNet MAE: 7.6
- VMamba accuracy: 91%
- Ensemble confidence: 0.89

## Regression

- ✓ Results within tolerance
- ✓ No performance degradation
```

---

**Last Updated**: 2024  
**Status**: Comprehensive testing guide
