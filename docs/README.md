# Project Documentation

Welcome to the Multi-Model Crowd Counting System documentation. This is a comprehensive system that combines **CSRNet** and **VMamba-TMTB** models for accurate crowd density prediction.

## 📚 Quick Navigation

- **[Quick Start](QUICK_START.md)** - Get up and running in 5 minutes
- **[Architecture](ARCHITECTURE.md)** - System design and model details
- **[API Reference](API.md)** - REST and WebSocket endpoints
- **[Deployment](DEPLOYMENT.md)** - Production setup guide
- **[Guides](guides/)** - In-depth tutorials and troubleshooting

## 🚀 What's Inside?

### Multi-Model Inference System

- **CSRNet**: Regression-based crowd counting with high accuracy
- **VMamba-TMTB**: State-of-the-art visual state space model
- **Ensemble Predictions**: Combined output for robust results
- **GPU Acceleration**: CUDA-enabled inference (RTX 3050 6GB)

### Features

- FastAPI REST API (Port 8000)
- WebSocket real-time streaming support
- IP camera support (HTTPS with mobile cameras)
- HLS video streaming pipeline
- TensorBoard training visualization

### Tech Stack

- **PyTorch**: 2.5.1+cu121 (GPU)
- **FastAPI**: Backend framework
- **React**: Frontend interface
- **OpenCV**: Computer vision processing
- **NumPy**: Numerical computing

## 📋 System Requirements

- Python 3.8+
- NVIDIA GPU (CUDA 12.1+) recommended
- 6GB VRAM minimum for inference
- 8GB+ for training

## 🔗 Important Directories

| Directory       | Purpose                               |
| --------------- | ------------------------------------- |
| `backend/`      | FastAPI server, API endpoints, models |
| `frontend/`     | React UI application                  |
| `ml/`           | Model training and utilities          |
| `tests/`        | Test suites and notebooks             |
| `docs/archive/` | Legacy documentation (for reference)  |

## 📖 Documentation Archive

Old documentation has been archived in `docs/archive/` for reference:

- Setup guides (legacy)
- Development progress
- Training documentation
- Model analysis
- Technical deep-dives

## ⚡ Getting Started

**For Users:**

1. Read [Quick Start](QUICK_START.md)
2. Review [API Reference](API.md)
3. Check [Deployment](DEPLOYMENT.md)

**For Developers:**

1. Read [Architecture](ARCHITECTURE.md)
2. Review [guides/testing.md](guides/testing.md)
3. Check [guides/training.md](guides/training.md)

## 🆘 Need Help?

Check out the [troubleshooting guide](guides/troubleshooting.md) for common issues and solutions.

---

**Last Updated**: 2024
**Status**: Production Ready
