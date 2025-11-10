# Backend Development Guide

This document provides all necessary information for developing and maintaining the Crowd Counting System backend.

## System Overview

- **Framework**: FastAPI (Python 3.8+)
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Cache**: Redis
- **Task Queue**: Celery
- **API Documentation**: Swagger UI at `/docs`
- **WebSocket**: Real-time updates

## Project Structure

```
backend/
├── app/
│   ├── api/               # API endpoints and routes
│   │   ├── v1/            # API versioning
│   │   └── __init__.py
│   │
│   ├── camera/            # Camera management
│   │   ├── camera.py      # Camera model and operations
│   │   └── __init__.py
│   │
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration management
│   │   ├── security.py    # Authentication & authorization
│   │   └── __init__.py
│   │
│   ├── services/          # Business logic
│   │   ├── prediction.py  # Model inference
│   │   └── __init__.py
│   │
│   ├── main.py           # FastAPI application
│   └── __init__.py
│
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── static/               # Static files
└── tests/                # Test suite
```

## Setup & Installation

### Prerequisites

- Python 3.8+
- Redis server
- FFmpeg
- CUDA (for GPU acceleration)

### 1. Environment Setup

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. Set up environment variables (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

### 2. Configuration

Edit `.env` file with your configuration:

```ini
# Server
APP_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./test.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Models
MODEL_PATH=./models
GPU_ENABLED=True
```

## API Documentation

### Base URL
- Development: `http://localhost:8000`
- Production: `https://your-production-url.com`

### Authentication
- JWT Token based authentication
- Required for protected endpoints
- Token lifetime: 24 hours

### Available Endpoints

#### 1. Authentication
- `POST /api/v1/auth/token` - Get access token
- `POST /api/v1/auth/refresh` - Refresh access token

#### 2. Camera Management
- `GET /api/v1/cameras` - List all cameras
- `POST /api/v1/cameras` - Add new camera
- `GET /api/v1/cameras/{camera_id}` - Get camera details
- `PUT /api/v1/cameras/{camera_id}` - Update camera
- `DELETE /api/v1/cameras/{camera_id}` - Remove camera

#### 3. Predictions
- `POST /api/v1/predict/{model}` - Get prediction
  - Models: `csrnet`, `vmamba`
  - Input: Image file
  - Output: Prediction results

#### 4. WebSocket
- `ws://localhost:8000/ws` - Real-time updates
  - Events: `connect`, `prediction`, `error`, `disconnect`

## Development Workflow

### 1. Running the Server

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_camera.py

# Run with coverage
pytest --cov=app tests/
```

### 3. Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document public methods with docstrings
- Keep functions small and focused

## Deployment

### 1. Production Setup

1. Set up a production-ready ASGI server:
   ```bash
   pip install gunicorn uvicorn[standard]
   ```

2. Create a systemd service:
   ```ini
   # /etc/systemd/system/crowd-counting.service
   [Unit]
   Description=Crowd Counting API
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/backend
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable crowd-counting
   sudo systemctl start crowd-counting
   ```

### 2. Monitoring

- Logs: `journalctl -u crowd-counting -f`
- Metrics: Prometheus endpoint at `/metrics`
- Health check: `/health`

## Troubleshooting

### Common Issues

1. **CUDA Errors**
   - Verify CUDA installation: `nvidia-smi`
   - Check PyTorch CUDA compatibility
   - Set `GPU_ENABLED=False` in `.env` if needed

2. **Memory Issues**
   - Reduce batch size
   - Enable model quantization
   - Use smaller input resolution

3. **API Errors**
   - Check server logs
   - Verify request format
   - Ensure required headers are set

## Contributing

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest`
4. Commit changes: `git commit -m "Add your feature"`
5. Push to the branch: `git push origin feature/your-feature`
6. Create a Pull Request

## License

[Your License Here]
