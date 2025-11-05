# System Architecture

## Overview

The Multi-Model Crowd Counting System is a production-ready solution combining two state-of-the-art deep learning models for accurate crowd density prediction:

1. **CSRNet** - Regression-based crowd counting with adaptive dilated convolutions
2. **VMamba-TMTB** - State-of-the-art visual state space model with temporal attention

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│                  Port: 3000                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    HTTP/WebSocket
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌──────────────────┐            ┌──────────────────────┐
│  Image Upload    │            │  IP Camera Stream    │
│  Local File      │            │  HTTPS/MJPEG         │
└────────┬─────────┘            └──────────┬───────────┘
         │                                 │
         └─────────────────┬───────────────┘
                           │
                    ▼
            ┌──────────────────────┐
            │  FastAPI Backend     │
            │  Port: 8000          │
            │  Uvicorn Server      │
            └─────┬────────┬────────┘
                  │        │
        ┌─────────┘        └─────────┐
        │                            │
        ▼                            ▼
    ┌────────┐                  ┌──────────┐
    │ CSRNet │                  │ VMamba   │
    │        │                  │  -TMTB   │
    │ Model  │                  │  Model   │
    └─┬──────┘                  └──┬───────┘
      │                            │
      │ Density Map               │ Density Map
      │ + Count                   │ + Count
      │                            │
      └─────────────┬──────────────┘
                    │
                    ▼
           ┌────────────────┐
           │ Ensemble       │
           │ Aggregation    │
           │ (Averaging)    │
           └────────┬───────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
    ┌──────────┐         ┌───────────┐
    │ JSON     │         │ HLS/MJPEG │
    │ Response │         │ Stream    │
    └──────────┘         └───────────┘
```

## Component Details

### Frontend (React)

- **Purpose**: User interface for image upload and visualization
- **Port**: 3000
- **Features**:
  - Image upload/selection
  - Real-time density map visualization
  - Stream preview
  - Result history

### Backend (FastAPI)

- **Purpose**: HTTP API server handling inference requests
- **Port**: 8000
- **Framework**: FastAPI with Uvicorn
- **Features**:
  - RESTful endpoints
  - WebSocket support for real-time streaming
  - Request validation
  - CORS support
  - Swagger API documentation

### Input Sources

1. **Direct Image Upload**

   - PNG, JPG, JPEG formats
   - Max size: Configurable (default 50MB)

2. **IP Camera Stream**

   - HTTPS support
   - MJPEG format
   - Mobile camera compatible

3. **Video Files**
   - MP4, AVI, MOV formats
   - Frame extraction and processing

### Models

#### CSRNet

```
Image → Conv2d → Dilated Conv Layers → Density Map
         (64ch)  (adaptive rates)     (1 channel)
```

- **Architecture**: Regression-based with dilated convolutions
- **Input**: RGB image (N, 3, H, W)
- **Output**: Density map (N, 1, H/8, W/8)
- **Strength**: Accurate counting on crowded scenes
- **Trained on**: ShanghaiTech dataset (parts A+B)

#### VMamba-TMTB

```
Image → Patch Embedding → Visual SSM → Density Prediction
        (Patch tokens)     Blocks      (with TMTB)
```

- **Architecture**: Vision State Space Model with Temporal Blocks
- **Input**: RGB image or temporal sequence
- **Output**: Density prediction with confidence
- **Strength**: Fast inference, good generalization
- **Type**: Pre-trained visual SSM

### Processing Pipeline

```
1. INPUT
   ↓
2. PREPROCESSING
   - Load image
   - Resize to model input size
   - Normalize (ImageNet stats)
   - Convert to tensor
   ↓
3. INFERENCE
   - CSRNet: Forward pass → density map
   - VMamba: Forward pass → density prediction
   ↓
4. POST-PROCESSING
   - Normalize outputs to [0, 1]
   - Upsample to original resolution
   - Generate visualizations
   ↓
5. AGGREGATION
   - Average predictions from both models
   - Calculate confidence score
   - Generate heatmap
   ↓
6. OUTPUT
   - JSON response with predictions
   - Density map image
   - Visualizations
```

## API Endpoints

### CSRNet Endpoint

```
POST /api/v1/csrnet/predict

Request:
{
  "image_url": "https://example.com/image.jpg",
  "visualize": true,
  "return_map": true
}

Response:
{
  "count": 157,
  "density": 0.82,
  "error": null,
  "heatmap": "base64_encoded_image",
  "processing_time": 0.234
}
```

### VMamba Endpoint

```
POST /api/v1/tmtb/predict

Request:
{
  "image_url": "https://example.com/image.jpg",
  "visualize": true
}

Response:
{
  "count": 159,
  "confidence": 0.91,
  "error": null,
  "visualization": "base64_encoded_image"
}
```

### Ensemble Endpoint

```
POST /api/v1/predict

Request:
{
  "image_url": "https://example.com/image.jpg",
  "models": ["csrnet", "tmtb"]
}

Response:
{
  "ensemble_count": 158,
  "csrnet_count": 157,
  "tmtb_count": 159,
  "confidence": 0.87,
  "processing_time": 0.345
}
```

## Data Flow

### Request Flow

```
Client Request
    ↓
FastAPI Validation
    ↓
Load Image/Frame
    ↓
Preprocessing
    ↓
GPU Transfer (if available)
    ↓
Model Inference
    ↓
Post-processing
    ↓
Response Formatting
    ↓
Return to Client
```

### Inference Architecture

```
┌─────────────────────────────────────┐
│ Input Image (3, H, W)               │
└────────────┬────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌─────────────┐  ┌──────────────┐
│   CSRNet    │  │  VMamba-TMTB │
│             │  │              │
│ Regression  │  │  State Space │
│ Based       │  │  Model       │
└──────┬──────┘  └───────┬──────┘
       │                 │
       ▼                 ▼
    Density Map      Density Map
    (1, H/8, W/8)    (1, H, W)
       │                 │
       └────────┬────────┘
                │
                ▼
        ┌───────────────┐
        │  Normalize    │
        │  Aggregate    │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Final Output  │
        │ - Count       │
        │ - Confidence  │
        │ - Heatmap     │
        └───────────────┘
```

## Technology Stack

### Deep Learning

- **PyTorch**: 2.5.1 (CUDA 12.1)
- **TorchVision**: 0.16.2 (for image transforms)
- **TensorBoard**: Training visualization

### Backend

- **FastAPI**: Modern async web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Python-Multipart**: File uploads

### Computer Vision

- **OpenCV**: Image processing (4.8.x-4.9.x)
- **NumPy**: Numerical operations (1.26.4)
- **Pillow**: Image manipulation

### Frontend

- **React**: 18.x UI framework
- **Axios**: HTTP client
- **D3.js**: Data visualization (optional)

## Performance Characteristics

### CSRNet

- **Input Size**: 640×480 typical
- **Output Size**: 80×60 density map
- **GPU Memory**: ~2GB
- **Inference Time**: ~50-100ms (GPU)
- **Accuracy (MAE)**: ~7.6 persons (ShanghaiTech B)

### VMamba-TMTB

- **Input Size**: 384×384 typical
- **Output Size**: Single density value
- **GPU Memory**: ~1.5GB
- **Inference Time**: ~30-50ms (GPU)
- **Accuracy**: High generalization

### Combined System

- **Total Memory**: ~4GB (both models)
- **Combined Inference**: ~150ms
- **Throughput**: ~6-7 FPS with preprocessing
- **GPU Utilization**: 70-85%

## Hardware Requirements

### Minimum (CPU Inference)

- CPU: Intel i7 or AMD Ryzen 7
- RAM: 16GB
- Storage: 20GB
- Speed: ~2-3 FPS

### Recommended (GPU Inference)

- GPU: NVIDIA RTX 3050 or better (6GB VRAM)
- CPU: Intel i7/i9 or AMD Ryzen 7/9
- RAM: 16GB+
- Storage: 20GB SSD
- Speed: ~6-7 FPS

### Optimal (High Performance)

- GPU: NVIDIA A100 or RTX 4090 (40GB VRAM)
- CPU: High-end workstation CPU
- RAM: 32GB+
- Storage: NVMe SSD
- Speed: ~30+ FPS

## Configuration

See [QUICK_START.md](QUICK_START.md) for configuration details.

Key settings in `config/config.yaml`:

- Model paths
- Batch size (default: 1)
- GPU settings
- Input preprocessing
- Output format

## Deployment Options

1. **Local Development**: See [QUICK_START.md](QUICK_START.md)
2. **Docker**: See [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Cloud**: AWS, GCP, Azure containers
4. **Edge**: ONNX/TensorRT optimization

## Security Considerations

- Input validation on all endpoints
- File size limits
- CORS configuration
- Rate limiting (optional)
- HTTPS support for IP cameras

## Monitoring & Logging

- Request/response logging
- Performance metrics
- Error tracking
- GPU utilization monitoring
- Model inference times

## Future Enhancements

- [ ] Model quantization (INT8)
- [ ] ONNX export for inference
- [ ] TensorRT optimization
- [ ] Multi-GPU support
- [ ] Distributed inference
- [ ] Real-time video streaming
- [ ] Mobile app support
- [ ] Model versioning/A-B testing

---

**Last Updated**: 2024  
**Status**: Production Ready  
**Version**: 1.0
