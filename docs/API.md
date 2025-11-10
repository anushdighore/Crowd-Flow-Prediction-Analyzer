# API Reference

Complete documentation of all REST API endpoints for the Multi-Model Crowd Counting System.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Response Format

All responses are JSON with the following structure:

```json
{
  "success": true,
  "data": {
    /* endpoint-specific data */
  },
  "error": null,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Error response:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Description of error"
  }
}
```

## Server Endpoints

### Health Check

```
GET /health
```

Check if server is running and responsive.

**Response:**

```json
{
  "status": "healthy",
  "gpu_available": true,
  "models_loaded": ["csrnet", "tmtb"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Server Info

```
GET /api/v1/info
```

Get server configuration and available models.

**Response:**

```json
{
  "version": "1.0.0",
  "backend": "FastAPI",
  "models": [
    {
      "name": "csrnet",
      "type": "regression",
      "input_size": [640, 480],
      "gpu_memory": "2GB",
      "inference_time_ms": 75
    },
    {
      "name": "tmtb",
      "type": "state_space",
      "input_size": [384, 384],
      "gpu_memory": "1.5GB",
      "inference_time_ms": 40
    },
    {
      "name": "yolo",
      "type": "object_detection",
      "input_size": [640, 640],
      "gpu_memory": "512MB",
      "inference_time_ms": 75
    }
  ],
  "gpu": {
    "available": true,
    "cuda_version": "12.1",
    "device_name": "NVIDIA RTX 3050"
  }
}
```

## CSRNet Endpoints

### Single Prediction

```
POST /api/v1/csrnet/predict
```

Get crowd count prediction using CSRNet model.

**Request:**

```json
{
  "image_url": "https://example.com/image.jpg",
  "visualize": true,
  "return_map": true,
  "threshold": 0.5
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `image_url` | string | Yes | URL or local path to image |
| `visualize` | boolean | No | Return visualization heatmap |
| `return_map` | boolean | No | Include density map in response |
| `threshold` | float | No | Confidence threshold (0-1) |

**Response:**

```json
{
  "count": 157,
  "density": 0.82,
  "error": null,
  "heatmap": "data:image/png;base64,iVBORw0KGgo...",
  "map": "data:image/png;base64,iVBORw0KGgo...",
  "confidence": 0.89,
  "processing_time_ms": 234,
  "image_size": [1920, 1080]
}
```

### Batch Prediction

```
POST /api/v1/csrnet/batch
```

Process multiple images at once.

**Request:**

```json
{
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "visualize": false
}
```

**Response:**

```json
[
  {
    "image": "image1.jpg",
    "count": 157,
    "error": null,
    "processing_time_ms": 234
  },
  {
    "image": "image2.jpg",
    "count": 142,
    "error": null,
    "processing_time_ms": 220
  }
]
```

## VMamba-TMTB Endpoints

### Single Prediction

```
POST /api/v1/tmtb/predict
```

Get crowd count prediction using VMamba-TMTB model.

**Request:**

```json
{
  "image_url": "https://example.com/image.jpg",
  "visualize": true,
  "method": "dense"
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `image_url` | string | Yes | URL or local path to image |
| `visualize` | boolean | No | Return visualization |
| `method` | string | No | Prediction method: "dense" or "sparse" |

**Response:**

```json
{
  "count": 159,
  "confidence": 0.91,
  "error": null,
  "visualization": "data:image/png;base64,iVBORw0KGgo...",
  "processing_time_ms": 184,
  "method": "dense"
}
```

### Batch Prediction

```
POST /api/v1/tmtb/batch
```

Process multiple images with VMamba.

**Request:**

```json
{
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "method": "dense"
}
```

## YOLOv8 Endpoints

YOLOv8 uses object detection for crowd counting, providing bounding boxes around detected people.

### Health Check

```
GET /api/v1/yolo/health
```

Check YOLO model status and availability.

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda:0",
  "gpu_memory_allocated": "512 MB"
}
```

### Single Prediction (Count)

```
POST /api/v1/yolo/count
```

Get crowd count prediction using YOLOv8 object detection.

**Request:**

```json
{
  "image_url": "https://example.com/image.jpg",
  "confidence_threshold": 0.5
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `image_url` | string | Yes | URL or local path to image |
| `confidence_threshold` | float | No | Minimum confidence score (0-1, default: 0.5) |

**Response:**

```json
{
  "count": 145,
  "boxes": [
    { "x1": 100, "y1": 50, "x2": 150, "y2": 200, "confidence": 0.95 },
    { "x1": 200, "y1": 100, "x2": 250, "y2": 250, "confidence": 0.92 }
  ],
  "confidence": 0.935,
  "processing_time_ms": 85,
  "image_size": [1920, 1080]
}
```

### Prediction Alias

```
POST /api/v1/yolo/predict
```

Alias for `/count` endpoint for consistency across models.

### Detailed Detection

```
POST /api/v1/yolo/detect
```

Get detailed detection output with visualization overlay.

**Request:**

```json
{
  "image_url": "https://example.com/image.jpg",
  "confidence_threshold": 0.5,
  "draw_boxes": true
}
```

**Response:**

```json
{
  "count": 145,
  "boxes": [
    { "x1": 100, "y1": 50, "x2": 150, "y2": 200, "confidence": 0.95 },
    { "x1": 200, "y1": 100, "x2": 250, "y2": 250, "confidence": 0.92 }
  ],
  "visualization": "data:image/png;base64,iVBORw0KGgo...",
  "average_confidence": 0.935,
  "processing_time_ms": 95,
  "image_size": [1920, 1080]
}
```

### Real-time Webcam

```
POST /api/v1/yolo/webcam
```

Optimized endpoint for real-time webcam stream processing.

**Request:**

```json
{
  "frame_data": "base64_encoded_image",
  "resize": true,
  "confidence_threshold": 0.6
}
```

**Response:**

```json
{
  "count": 145,
  "boxes": [{ "x1": 100, "y1": 50, "x2": 150, "y2": 200, "confidence": 0.95 }],
  "confidence": 0.935,
  "processing_time_ms": 65,
  "frame_size": [1280, 720]
}
```

### Batch Processing

```
POST /api/v1/yolo/batch
```

Process multiple images at once.

**Request:**

```json
{
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
  ],
  "confidence_threshold": 0.5
}
```

**Response:**

```json
{
  "results": [
    {
      "image": "image1.jpg",
      "count": 145,
      "boxes": 145,
      "average_confidence": 0.935,
      "processing_time_ms": 85
    },
    {
      "image": "image2.jpg",
      "count": 128,
      "boxes": 128,
      "average_confidence": 0.912,
      "processing_time_ms": 82
    },
    {
      "image": "image3.jpg",
      "count": 156,
      "boxes": 156,
      "average_confidence": 0.928,
      "processing_time_ms": 88
    }
  ],
  "total_time_ms": 255
}
```

### Model Information

```
GET /api/v1/yolo/info
```

Get YOLOv8 model details and comparison with other models.

**Response:**

```json
{
  "model": "YOLOv8",
  "version": "8.0",
  "type": "object_detection",
  "input_size": [640, 640],
  "gpu_memory": "512 MB",
  "avg_inference_time_ms": 75,
  "approach": "Bounding box detection",
  "strengths": [
    "Accurate localization",
    "Detects individual people",
    "Fast inference",
    "Works in crowded scenes"
  ],
  "weaknesses": [
    "May miss partially occluded people",
    "Slower than regression methods in very dense crowds"
  ],
  "best_for": "Scenarios requiring individual person tracking or box coordinates",
  "comparison": {
    "csrnet": {
      "name": "CSRNet",
      "type": "density_regression",
      "avg_inference_time_ms": 75,
      "advantage": "Better for very dense crowds"
    },
    "tmtb": {
      "name": "VMamba-TMTB",
      "type": "state_space",
      "avg_inference_time_ms": 40,
      "advantage": "Fastest inference, best real-time performance"
    }
  }
}
```

## Ensemble Endpoints

### Combined Prediction

```
POST /api/v1/predict
```

Get predictions from all available models with ensemble voting.

**Request:**

```json
{
  "image_url": "https://example.com/image.jpg",
  "models": ["csrnet", "tmtb", "yolo"],
  "aggregation": "average",
  "visualize": true
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `image_url` | string | Yes | Image URL |
| `models` | array | No | Models to use (default: all) Options: csrnet, tmtb, yolo |
| `aggregation` | string | No | Method: "average", "median", "max", "weighted" |
| `visualize` | boolean | No | Return visualizations |

**Response:**

```json
{
  "ensemble_count": 143,
  "ensemble_confidence": 0.92,
  "predictions": [
    {
      "model": "csrnet",
      "count": 157,
      "confidence": 0.89
    },
    {
      "model": "tmtb",
      "count": 159,
      "confidence": 0.91
    },
    {
      "model": "yolo",
      "count": 145,
      "confidence": 0.935,
      "boxes": 145
    }
  ],
  "heatmap": "data:image/png;base64,iVBORw0KGgo...",
  "processing_time_ms": 235
}
```

## Video Streaming Endpoints

### HLS Stream

```
GET /stream/hls/{stream_id}/playlist.m3u8
```

Get HLS playlist for video streaming.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `stream_id` | string | Stream identifier |

**Response:** M3U8 playlist file

### MJPEG Stream

```
GET /stream/mjpeg/{stream_id}
```

Get MJPEG stream with real-time predictions overlay.

**Response:** Continuous MJPEG stream

## Webhook Endpoints

### Register Webhook

```
POST /api/v1/webhooks
```

Register a webhook for async result notifications.

**Request:**

```json
{
  "url": "https://your-service.com/webhook",
  "events": ["prediction_complete"],
  "model": "csrnet"
}
```

**Response:**

```json
{
  "webhook_id": "wh_12345",
  "status": "active",
  "url": "https://your-service.com/webhook"
}
```

### Trigger Async Prediction

```
POST /api/v1/predict/async
```

Start async prediction job.

**Request:**

```json
{
  "image_url": "https://example.com/image.jpg",
  "webhook_id": "wh_12345"
}
```

**Response:**

```json
{
  "job_id": "job_67890",
  "status": "queued",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Check Job Status

```
GET /api/v1/jobs/{job_id}
```

Get async job status and results.

**Response:**

```json
{
  "job_id": "job_67890",
  "status": "completed",
  "result": {
    /* prediction result */
  },
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:30Z"
}
```

## File Upload Endpoints

### Upload Image

```
POST /api/v1/upload
```

Upload image file directly (multipart/form-data).

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `file` | file | Image file (PNG, JPG, JPEG) |
| `model` | string | Model to use |

**Response:**

```json
{
  "file_id": "file_abc123",
  "filename": "image.jpg",
  "size": 524288,
  "upload_time": 1234
}
```

### Predict on Uploaded File

```
POST /api/v1/predict/{file_id}
```

Run prediction on previously uploaded file.

**Request:**

```json
{
  "model": "csrnet",
  "visualize": true
}
```

## Configuration Endpoints

### Get Configuration

```
GET /api/v1/config
```

Get current system configuration.

**Response:**

```json
{
  "models": {
    "csrnet": {
      "enabled": true,
      "weights": "/models/csrnet.pth",
      "input_size": [640, 480]
    },
    "tmtb": {
      "enabled": true,
      "weights": "/models/tmtb.pth",
      "input_size": [384, 384]
    }
  },
  "gpu": {
    "enabled": true,
    "device": 0
  }
}
```

### Update Configuration

```
PATCH /api/v1/config
```

Update system settings (admin only).

**Request:**

```json
{
  "gpu": {
    "enabled": true,
    "device": 0
  },
  "batch_size": 2
}
```

## Error Codes

| Code             | HTTP | Description                |
| ---------------- | ---- | -------------------------- |
| `INVALID_INPUT`  | 400  | Invalid request parameters |
| `FILE_NOT_FOUND` | 404  | Image file not found       |
| `MODEL_ERROR`    | 500  | Model inference error      |
| `GPU_ERROR`      | 500  | GPU operation failed       |
| `TIMEOUT`        | 504  | Request timeout            |
| `RATE_LIMITED`   | 429  | Too many requests          |

## Rate Limiting

Default limits:

- 100 requests per minute (general)
- 10 concurrent uploads
- 5 concurrent processing jobs

## Pagination

List endpoints support pagination:

```
GET /api/v1/results?page=1&limit=20
```

**Response:**

```json
{
  "data": [
    /* items */
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

## Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Get server info
curl http://localhost:8000/api/v1/info

# Predict with CSRNet
curl -X POST http://localhost:8000/api/v1/csrnet/predict \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "visualize": true
  }'

# Upload and predict
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@image.jpg" \
  -F "model=csrnet"
```

## Swagger UI

Interactive API documentation available at:

```
http://localhost:8000/docs
```

## WebSocket Endpoints

### Real-time Predictions

```
WebSocket /ws/predict
```

Connect for real-time prediction updates.

**Message Format:**

```json
{
  "action": "predict",
  "image_url": "https://example.com/image.jpg",
  "model": "csrnet"
}
```

---

**API Version**: 1.0  
**Last Updated**: 2024  
**Documentation**: [FastAPI Docs](http://localhost:8000/docs)
