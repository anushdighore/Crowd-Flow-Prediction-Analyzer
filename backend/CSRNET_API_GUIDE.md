# Backend API - CSRNet Integration

## 🎯 Overview

The backend API connects the CSRNet model from the ML package to the FastAPI server, enabling crowd counting inference through REST endpoints.

## 📁 Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── csrnet.py            # CSRNet endpoints
│   └── core/
│       ├── config.py                    # Configuration loader
│       └── settings.py                  # Settings (from .env)
│
├── config/                              # YAML configs
├── target/                              # Cache directory
├── .env                                 # Environment variables
├── pyproject.toml                       # Package config
├── start_backend.bat                    # Startup script
└── README.md
```

## 🔌 API Endpoints

### Base URL: `http://localhost:8000`

### 1. Root

```
GET /
```

Returns API information and available models.

### 2. Health Check

```
GET /health
```

Overall API health status.

### 3. CSRNet Health

```
GET /api/v1/csrnet/health
```

CSRNet model status and device information.

### 4. Count Crowd (CSRNet)

```
POST /api/v1/csrnet/count
Content-Type: multipart/form-data
```

**Request:**

- `file`: Image file (JPEG, PNG, etc.)

**Response:**

```json
{
  "success": true,
  "model": "CSRNet",
  "count": 42,
  "statistics": {
    "count": 42,
    "min": 0.0,
    "max": 0.85,
    "mean": 0.12,
    "std": 0.18,
    "shape": [64, 64]
  },
  "image_size": "512x384",
  "filename": "crowd.jpg"
}
```

### 5. Count with Heatmap

```
POST /api/v1/csrnet/count-with-heatmap
Content-Type: multipart/form-data
```

**Response includes base64-encoded heatmap image:**

```json
{
  "success": true,
  "model": "CSRNet",
  "count": 42,
  "statistics": {...},
  "heatmap": "iVBORw0KGgoAAAANSUhEUgAA...",
  "image_size": "512x384",
  "filename": "crowd.jpg"
}
```

## 🚀 Quick Start

### 1. Start the Server

**Windows:**

```cmd
cd backend
start_backend.bat
```

**Linux/Mac:**

```bash
cd backend
./start_backend.sh
```

**Or manually:**

```bash
cd backend
set PYTHONPYCACHEPREFIX=target/pycache  # Windows
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test the API

**Using curl:**

```bash
# Health check
curl http://localhost:8000/health

# CSRNet health
curl http://localhost:8000/api/v1/csrnet/health

# Count people
curl -X POST \
  -F "file=@path/to/image.jpg" \
  http://localhost:8000/api/v1/csrnet/count
```

**Using Python:**

```python
import requests

url = "http://localhost:8000/api/v1/csrnet/count"

with open("crowd.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print(response.json())
# {"success": true, "count": 42, ...}
```

**Using JavaScript (Frontend):**

```javascript
const formData = new FormData();
formData.append("file", file);

const response = await fetch("http://localhost:8000/api/v1/csrnet/count", {
  method: "POST",
  body: formData,
});

const result = await response.json();
console.log(result.count); // 42
```

### 3. Access API Documentation

Open in browser:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Paths
ML_MODELS_PATH=../ml
CHECKPOINTS_PATH=../ml/checkpoints

# Model
DEFAULT_MODEL=csrnet
DEVICE=cuda  # or 'cpu'
```

### Checkpoint Location

The CSRNet checkpoint should be at:

```
ml/checkpoints/csrnet.pth
```

If the checkpoint is elsewhere, update the path in:

```python
# backend/app/api/v1/endpoints/csrnet.py
checkpoint_path = Path(...) / "ml" / "checkpoints" / "csrnet.pth"
```

## 🐛 Troubleshooting

### Model Not Loading

**Error:** `FileNotFoundError: CSRNet checkpoint not found`

**Solution:**

```bash
# Check if checkpoint exists
ls ../ml/checkpoints/csrnet.pth

# If not, download or copy checkpoint to:
# ml/checkpoints/csrnet.pth
```

### Import Errors

**Error:** `Import "models.csrnet.csrnet" could not be resolved`

**Solution:**

```python
# The endpoint adds ML path dynamically:
ml_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "src"
sys.path.insert(0, str(ml_path))
```

This is handled automatically in the code.

### CUDA Out of Memory

**Error:** `RuntimeError: CUDA out of memory`

**Solution:**

```env
# In .env, change to CPU:
DEVICE=cpu
```

### CORS Errors from Frontend

**Error:** `Access to fetch at 'http://localhost:8000' blocked by CORS`

**Solution:**

```python
# In app/main.py, add your frontend URL:
allow_origins=[
    "http://localhost:3000",     # React
    "http://localhost:5173",     # Vite
    "your-frontend-url"          # Add here
]
```

## 📊 Model Flow

```
Frontend Upload
    ↓
Backend API (/api/v1/csrnet/count)
    ↓
1. Load image from bytes
    ↓
2. Preprocess (CSRNetPreprocessor)
   - ToTensor
   - ImageNet Normalization
    ↓
3. Model Inference (CSRNet)
   - Forward pass
   - Generate density map
    ↓
4. Postprocess (CSRNetPostprocessor)
   - Density map → count
   - Generate statistics
    ↓
5. Return JSON response
    ↓
Frontend Display
```

## 🧪 Testing

### Manual Testing

1. Start server: `start_backend.bat`
2. Open: http://localhost:8000/docs
3. Try `/api/v1/csrnet/health` endpoint
4. Upload test image to `/api/v1/csrnet/count`

### Automated Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

## 📝 Next Steps

1. ✅ CSRNet backend API is ready
2. ⏳ Update frontend to call `/api/v1/csrnet/count`
3. ⏳ Test end-to-end flow
4. ⏳ Add more models (VMamba, MCNN)
5. ⏳ Add authentication (if needed)
6. ⏳ Deploy to production

## 🔗 Related Files

- **ML Model:** `ml/src/models/csrnet/csrnet.py`
- **Preprocessing:** `ml/src/pipelines/preprocessing/csrnet_preprocess.py`
- **Postprocessing:** `ml/src/pipelines/postprocessing/csrnet_postprocess.py`
- **API Endpoint:** `backend/app/api/v1/endpoints/csrnet.py`
- **Main App:** `backend/app/main.py`

---

✨ **Your CSRNet backend API is now ready to serve predictions!**
