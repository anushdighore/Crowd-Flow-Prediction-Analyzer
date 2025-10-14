# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a **Crowd Flow Prediction & Analysis System** - a production-ready, multi-model crowd counting and flow analysis system built with modern ML engineering practices. It features real-time webcam processing, multiple state-of-the-art models (CSRNet and TMTB/VMamba), and a config-driven architecture.

### Key Technologies
- **Backend**: FastAPI with Python 3.9+, PyTorch, OpenCV
- **Frontend**: React 19+, WebSocket API for real-time processing
- **ML Models**: CSRNet (16.2M params), TMTB/VMamba (88.7M params)
- **Configuration**: YAML + Pydantic validation
- **Environment**: Conda-based (`crowdenv`)

## Architecture

The system follows a layered architecture:
- **UI Layer**: React frontend (port 3000) with upload/webcam/external camera/HLS modes
- **API Layer**: FastAPI backend (port 8000) with REST and WebSocket endpoints
- **Config Layer**: YAML configurations with Pydantic validation
- **ML Layer**: PyTorch models with GPU/CPU optimization

### Data Flow
1. **Upload Mode**: HTTP POST → config-driven resizing → model inference → results
2. **Webcam Mode**: WebSocket stream → real-time processing → live FPS metrics
3. **External Camera**: IP camera integration → ML predictions → frame streaming
4. **HLS Streaming**: FFmpeg-based HLS packaging for camera streams

## Common Development Commands

### Environment Setup
```bash
# Activate conda environment (required for all operations)
conda activate crowdenv

# Install dependencies
pip install -r requirements.txt  # Root dependencies
pip install -r backend/requirements.txt  # Backend specific
cd frontend && npm install  # Frontend dependencies
```

### Starting the Application
```bash
# Start both services (Windows)
start_app.bat

# Or manually start backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or manually start frontend
cd frontend
npm start
```

### Development & Testing
```bash
# Backend development with hot reload
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
npm start

# Run backend tests
cd backend
python -m pytest tests/ -v

# Build frontend for production
cd frontend
npm run build
```

### Model Operations
```bash
# Test model loading
python -c "from ml.src.models.csrnet import api as csrnet_api; print('CSRNet OK')"
python -c "from ml.src.models.tmtb import api as tmtb_api; print('TMTB OK')"

# Check GPU availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Fine-tune VMamba model (if needed)
python finetune_vmamba.py
```

### Configuration Management
```bash
# Validate configurations
python -c "from ml.src.core.config_loader import load_csrnet_config; print('Config OK')"

# Test configuration changes (no restart needed - configs are cached)
# Edit: ml/config/csrnet_config.yaml or ml/config/tmtb_config.yaml
```

## Project Structure

### Key Directories
- `backend/`: FastAPI application with API endpoints and WebSocket handlers
- `frontend/`: React application with model selection and real-time interfaces  
- `ml/`: Machine learning core with model implementations and configurations
  - `ml/src/models/csrnet/`: CSRNet implementation and API wrapper
  - `ml/src/models/tmtb/`: TMTB/VMamba implementation with fine-tuning
  - `ml/config/`: Model-specific YAML configurations
  - `ml/checkpoints/`: Pre-trained model weights
- `docs/`: Comprehensive documentation organized by category
- `scripts/`: Utility scripts for dependencies and testing

### Model Integration Pattern
Each model follows a standardized API pattern:
```python
# All models expose: predict(image, source="webcam|image|video|surveillance")
result = model_api.predict(image, source="webcam")
# Returns: count, inference_time_ms, device, dimensions, etc.
```

### Configuration System
- **YAML-based**: Model settings per input source (webcam vs upload vs surveillance)
- **Pydantic validation**: Type-safe configuration with bounds checking
- **LRU caching**: Configurations cached for performance (`@lru_cache`)
- **Source-specific resizing**: Different dimensions for different input types

Example config structure:
```yaml
preprocessing:
  image:     # Upload source - high quality
    length: 800
    breadth: 800
  webcam:    # Real-time source - optimized 
    length: 640
    breadth: 640
```

## API Endpoints

### REST API
- `GET /api/v1/{model}/health` - Model health check
- `POST /api/v1/{model}/count` - Image upload counting
- `GET /health` - Application health status

### WebSocket API
- `WS /ws/count` - Real-time webcam counting
- `WS /ws/external-camera` - External IP camera processing

### Camera & Streaming
- `GET /api/camera/test-connection` - Test camera connectivity
- `POST /api/camera/hls/start` - Start HLS streaming
- `GET /api/camera/hls/playlist/{stream_id}/playlist.m3u8` - HLS manifest

## Performance Considerations

### Model Performance
- **CSRNet**: ~50-100ms inference, 10-15 FPS webcam, ~1.2GB GPU memory
- **TMTB**: ~100-200ms inference, 5-10 FPS webcam, ~3.5GB GPU memory
- **Loading optimization**: CPU-first loading for TMTB (560x faster than original)

### Configuration-Driven Optimization
- **Webcam**: Reduced resolution for real-time performance (CSRNet: 640x640, TMTB: 384x384)
- **Upload**: High resolution for accuracy (800x800)
- **Aspect ratio preservation**: Smart resizing prevents distortion

## Development Patterns

### Adding New Models
1. Create `ml/src/models/new_model/` directory
2. Implement `api.py` with `predict()` function following existing pattern
3. Add `ml/config/new_model_config.yaml` with preprocessing settings
4. Update `ml/src/core/config_loader.py` with new config loader
5. Add API endpoints in `backend/app/api/v1/endpoints/new_model.py`
6. Update frontend model selector in `frontend/src/App.js`

### Configuration Experiments
- Edit YAML files directly (changes auto-reload due to `@lru_cache`)
- Test different dimensions for performance vs accuracy trade-offs
- No backend restart required for config changes

### Error Handling Patterns
- Comprehensive error reporting throughout the pipeline
- GPU memory management with automatic cleanup
- Graceful fallback to CPU when GPU unavailable
- WebSocket connection error recovery

## Troubleshooting

### Common Issues
**Backend won't start**: Check conda environment activation and port 8000 availability
**Model loading errors**: Verify model files in `ml/checkpoints/` and CUDA availability  
**Frontend CORS errors**: Ensure backend running on localhost:8000
**Poor performance**: Check GPU memory usage, reduce webcam resolution in config

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Model-specific health
curl http://localhost:8000/api/v1/csrnet/health
curl http://localhost:8000/api/v1/tmtb/health

# Camera connectivity (if using external cameras)
curl "http://localhost:8000/api/camera/test-connection?camera_url=http://192.168.1.6:8080"
```

## Development Environment

### Required Software
- Python 3.9+ with conda
- Node.js 16+ for frontend
- CUDA 12.1 compatible GPU (optional, CPU fallback available)
- FFmpeg (for HLS streaming features)

### Environment Variables
The application uses a conda environment named `crowdenv`. All Python commands must be run within this environment.

### File Paths (Windows-specific)
This project is currently configured for Windows development with batch scripts for startup. Path separators and batch files are Windows-specific.