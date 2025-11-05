# Quick Start Guide

Get the Multi-Model Crowd Counting System up and running in minutes!

## Prerequisites

- Python 3.8+
- pip or conda package manager
- NVIDIA GPU with CUDA 12.1+ (optional but recommended)

## Installation (5 minutes)

### 1. Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Or with conda:
conda env create -f environment.yaml
conda activate crowd-counting
```

### 2. Configure Backend

```bash
# Copy configuration
cp config/config.yaml.example config/config.yaml

# Update config.yaml with your settings (optional)
# Default settings work out of the box
```

### 3. Start Backend Server

```bash
# From backend directory
python run.py

# Or use the startup script
./start_backend.sh  # Linux/Mac
./start_backend.bat  # Windows
```

Server runs on: `http://localhost:8000`

API Docs: `http://localhost:8000/docs` (Swagger UI)

### 4. Start Frontend (Optional)

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend runs on: `http://localhost:3000`

## Testing Your Setup

### Quick API Test

```bash
# Test CSRNet endpoint
curl -X POST http://localhost:8000/api/v1/csrnet/predict \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'

# Check server health
curl http://localhost:8000/health
```

### Python Test

```python
import requests
import json

# Test CSRNet
response = requests.post(
    'http://localhost:8000/api/v1/csrnet/predict',
    json={'image_url': 'https://example.com/image.jpg'}
)
print(response.json())
```

## Using with IP Camera

```python
import requests
import cv2

# IP camera stream URL
camera_url = 'https://192.168.1.6:8080/shot.jpg'

# Get frame
response = requests.get(camera_url, verify=False)
nparr = np.frombuffer(response.content, np.uint8)
img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

# Send to API
response = requests.post(
    'http://localhost:8000/api/v1/csrnet/predict',
    json={'image_path': img}
)
```

## API Endpoints

### CSRNet Predictions

- **POST** `/api/v1/csrnet/predict` - Single image prediction
- **POST** `/api/v1/csrnet/batch` - Batch predictions

### VMamba-TMTB Predictions

- **POST** `/api/v1/tmtb/predict` - Single image prediction
- **POST** `/api/v1/tmtb/batch` - Batch predictions

### Server Info

- **GET** `/health` - Health check
- **GET** `/api/v1/info` - System information

See [API Reference](API.md) for detailed documentation.

## Troubleshooting

### GPU Not Detected

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False, reinstall PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Port Already in Use

```bash
# Change port in config.yaml
# Default: 8000
# Then restart server
```

### Module Not Found Errors

```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Verify installation
python -c "import torch, cv2, fastapi; print('All imports OK')"
```

### Memory Issues

Adjust in `config/config.yaml`:

- Reduce `batch_size` (default: 1)
- Reduce `max_workers` for DataLoader
- Enable `mixed_precision` (default: true)

## Next Steps

1. **Read the [Architecture](ARCHITECTURE.md)** to understand the system design
2. **Explore [API Reference](API.md)** for all available endpoints
3. **Check [Deployment Guide](DEPLOYMENT.md)** for production setup
4. **Review [guides/](guides/)** for advanced topics

## Key Files

| File                         | Purpose                    |
| ---------------------------- | -------------------------- |
| `backend/run.py`             | Start FastAPI server       |
| `backend/config/config.yaml` | Configuration settings     |
| `backend/app/main.py`        | Application initialization |
| `ml/src/csrnet/`             | CSRNet model code          |
| `ml/src/models/tmtb/`        | VMamba-TMTB model code     |

## Support

- Check [troubleshooting guide](guides/troubleshooting.md) for common issues
- Review [archived docs](archive/) for legacy setup guides
- Open an issue on GitHub with error details

---

**Status**: ✅ Ready to use  
**Last Updated**: 2024  
**Tested on**: Python 3.10, PyTorch 2.5.1, CUDA 12.1
