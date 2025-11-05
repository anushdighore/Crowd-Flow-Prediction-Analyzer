# Product Requirements Document (PRD)
## Multi-Model Crowd Counting System

**Document Version**: 1.0  
**Last Updated**: November 2024  
**Status**: Production Ready  
**Project Owner**: Crowd Flow Prediction Analyzer Team

---

## Executive Summary

The **Multi-Model Crowd Counting System** is an AI-powered solution that leverages state-of-the-art deep learning models (CSRNet and VMamba-TMTB) to accurately predict crowd density and count people in images and video streams. The system provides both REST API and real-time WebSocket interfaces for integration with existing surveillance and monitoring infrastructure.

### Key Value Proposition
- **Dual-model ensemble** for robust predictions
- **Real-time processing** with GPU acceleration
- **Multi-source input** support (images, webcams, IP cameras, video files)
- **Production-ready** with comprehensive API documentation
- **Scalable architecture** supporting distributed deployment

---

## 1. Product Overview

### 1.1 Problem Statement

Modern surveillance and crowd management systems lack accurate, scalable solutions for real-time crowd counting and density prediction. Existing solutions often suffer from:
- Limited accuracy on diverse scenes and lighting conditions
- Single-model dependency (no fallback options)
- High false positive/negative rates
- Expensive hardware requirements

### 1.2 Solution

A multi-model ensemble system combining:
- **CSRNet** (Regression-based, high accuracy on dense crowds)
- **VMamba-TMTB** (State-space model, excellent generalization)

Providing:
- Dual predictions for robustness
- Ensemble averaging for improved accuracy
- Fast inference with GPU optimization
- Simple REST API + WebSocket for real-time updates

### 1.3 Target Users

1. **Event Management Companies** - Monitor crowd levels at venues
2. **Retail & Shopping Malls** - Track foot traffic and occupancy
3. **Public Safety Departments** - Monitor public gatherings
4. **Smart City Initiatives** - Real-time crowd analytics
5. **Research Institutions** - Benchmark crowd counting models

---

## 2. Product Features

### 2.1 Core Features

#### A. Multi-Model Inference Engine
- **CSRNet Model**
  - Regression-based architecture with adaptive dilated convolutions
  - Specialized for dense crowd scenarios
  - Input: 640×480 RGB images
  - Output: Density map (1/8 resolution) + Count estimate
  - Latency: ~75ms on RTX 3050

- **VMamba-TMTB Model**
  - Visual State Space Model with Temporal Blocks
  - Superior generalization to unseen scenes
  - Input: 384×384 RGB images
  - Output: Count prediction + Confidence score
  - Latency: ~40ms on RTX 3050

- **Ensemble Voting**
  - Averages predictions from both models
  - Confidence score calculation
  - Weighted averaging option (configurable)

#### B. Input Processing
- **Image Upload** (PNG, JPG, JPEG)
  - Maximum size: 50MB (configurable)
  - Automatic resizing and normalization
  - Batch processing support

- **Live Camera Feeds**
  - IP camera support (HTTPS, MJPEG)
  - Mobile camera integration
  - Multiple simultaneous streams

- **Video File Processing**
  - MP4, AVI, MOV formats
  - Frame extraction at configurable FPS
  - Batch inference mode

#### C. Output & Visualization
- **JSON Response**
  ```json
  {
    "count": 158,
    "confidence": 0.90,
    "csrnet_count": 157,
    "tmtb_count": 159,
    "processing_time_ms": 425,
    "heatmap": "base64_encoded_image"
  }
  ```

- **Heatmap Visualization**
  - Density map overlay on original image
  - Color-coded visualization (cool to warm)
  - Multiple visualization styles

- **HLS/MJPEG Streaming**
  - Real-time stream with predictions overlay
  - Adaptive bitrate streaming
  - Browser-compatible formats

#### D. API Interfaces
- **REST API** (Primary)
  - 20+ documented endpoints
  - Request/response validation
  - Error handling with meaningful codes
  - Rate limiting (100 req/min default)

- **WebSocket API** (Real-time)
  - Streaming predictions
  - Low-latency updates (~100ms)
  - Bidirectional communication
  - Automatic reconnection

- **Webhook Integration**
  - Async result notifications
  - Customizable event triggers
  - Payload customization

### 2.2 Advanced Features

#### A. Training & Fine-tuning
- Dataset preparation utilities
- ShanghaiTech dataset support
- Custom dataset integration
- Training monitoring with TensorBoard
- Model checkpointing and versioning

#### B. Performance Optimization
- Mixed precision training (FP16)
- Gradient accumulation
- Data parallel processing
- Model quantization support (INT8)
- TensorRT optimization

#### C. Monitoring & Observability
- Prometheus metrics export
- Performance tracking (latency, throughput)
- GPU utilization monitoring
- Error rate tracking
- Request logging

#### D. Security Features
- API key authentication (optional)
- HTTPS/SSL support
- CORS configuration
- Rate limiting
- Request validation

---

## 3. Technical Specifications

### 3.1 System Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend (React)              │
│            Port 3000 - UI & Dashboard           │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/WebSocket
┌──────────────────┴──────────────────────────────┐
│            FastAPI Backend (Port 8000)          │
│  ├─ REST API (/api/v1/)                         │
│  ├─ WebSocket (/ws/)                           │
│  ├─ Health Check (/health)                      │
│  └─ Prometheus Metrics (/metrics)               │
└──────────┬──────────────────────────┬───────────┘
           │                          │
      ┌────▼────┐              ┌──────▼────┐
      │ CSRNet  │              │  VMamba   │
      │ Model   │              │   -TMTB   │
      │(GPU)    │              │  (GPU)    │
      └────┬────┘              └──────┬────┘
           │                          │
           └──────────┬───────────────┘
                      │
           ┌──────────▼──────────┐
           │ Ensemble Voting     │
           │ (Average/Median)    │
           └─────────────────────┘
```

### 3.2 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Deep Learning** | PyTorch | 2.5.1+cu121 |
| **GPU Support** | CUDA | 12.1 |
| **Image Processing** | OpenCV | 4.8-4.9 |
| **Numerical** | NumPy | 1.26.4 |
| **Backend Framework** | FastAPI | Latest |
| **ASGI Server** | Uvicorn | Latest |
| **Frontend** | React | 18.x |
| **Database** | PostgreSQL | 13+ (optional) |
| **Cache** | Redis | 6+ (optional) |
| **Containerization** | Docker | 20.x |
| **Orchestration** | Kubernetes | 1.24+ (optional) |

### 3.3 Performance Specifications

| Metric | Specification |
|--------|---------------|
| **CSRNet Latency** | 50-100ms (GPU) |
| **VMamba Latency** | 30-50ms (GPU) |
| **Ensemble Latency** | 100-150ms (GPU) |
| **Throughput** | 6-8 FPS (GPU) |
| **Accuracy (MAE)** | 7.6 (ShanghaiTech B) |
| **GPU Memory** | 4-6GB (both models) |
| **Batch Size** | 1-4 (configurable) |
| **Concurrency** | 10-20 simultaneous requests |

### 3.4 Hardware Requirements

#### Minimum (CPU Inference)
- CPU: Intel i7 / AMD Ryzen 7
- RAM: 16GB
- Storage: 20GB SSD
- Processing: 2-3 FPS

#### Recommended (GPU Inference)
- GPU: NVIDIA RTX 3050 (6GB VRAM)
- CPU: Modern multi-core processor
- RAM: 16GB+
- Storage: 20GB SSD
- Processing: 6-8 FPS

#### Optimal (High Performance)
- GPU: NVIDIA A100 / RTX 4090
- CPU: High-end workstation
- RAM: 32GB+
- Storage: NVMe SSD
- Processing: 30+ FPS

---

## 4. Functional Requirements

### 4.1 User Stories

#### Story 1: Event Manager
**As a** security manager at a large venue  
**I want to** monitor real-time crowd density  
**So that** I can respond quickly to overcrowding situations

**Acceptance Criteria:**
- System processes live camera feed with <500ms latency
- Crowd count updates every 1 second
- Alerts trigger when crowd density exceeds threshold
- Multiple camera support

#### Story 2: Data Scientist
**As a** researcher  
**I want to** fine-tune models on custom datasets  
**So that** I can improve accuracy for specific scenarios

**Acceptance Criteria:**
- Easy dataset upload interface
- Training progress visualization
- Model comparison tools
- Export trained models in standard formats

#### Story 3: Developer
**As an** integration engineer  
**I want to** integrate crowd counting into my app  
**So that** I can add crowd analytics to my platform

**Acceptance Criteria:**
- Clear API documentation with examples
- SDKs for Python, JavaScript
- Webhook support for async processing
- Sandbox environment for testing

### 4.2 Functional Requirements

#### F1: Prediction Engine
- [x] Load and manage multiple ML models
- [x] Perform single image inference
- [x] Perform batch inference
- [x] Ensemble predictions from multiple models
- [x] Return predictions with confidence scores
- [x] Support both CPU and GPU inference

#### F2: Input Handling
- [x] Accept image uploads (REST endpoint)
- [x] Accept image URLs
- [x] Stream from IP cameras
- [x] Webcam integration
- [x] Video file processing
- [x] Batch processing multiple files

#### F3: Output Generation
- [x] JSON response with predictions
- [x] Density heatmap generation
- [x] Visualization with overlay
- [x] HLS streaming output
- [x] MJPEG streaming output
- [x] Base64 encoded images in response

#### F4: API Server
- [x] REST endpoints for predictions
- [x] Health check endpoint
- [x] Server info endpoint
- [x] Metrics/monitoring endpoint
- [x] CORS support
- [x] Request validation
- [x] Error handling

#### F5: Real-time Features
- [x] WebSocket endpoint for streaming
- [x] Live camera feed processing
- [x] Real-time result updates
- [x] Configurable update intervals

#### F6: Configuration Management
- [x] YAML config file support
- [x] Environment variable overrides
- [x] Model path configuration
- [x] API port configuration
- [x] GPU device selection
- [x] Batch size tuning

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **Response Time**: <500ms for single image prediction
- **Throughput**: 6-8 FPS on GPU
- **Latency**: <100ms model inference (ensemble)
- **Concurrent Users**: Support 10-20 simultaneous requests
- **Availability**: 99.5% uptime SLA

### 5.2 Scalability
- **Horizontal Scaling**: Load balancer support
- **Vertical Scaling**: Multi-GPU support
- **Data Parallelism**: Distributed inference
- **Database**: Support for multiple concurrent connections

### 5.3 Reliability
- **Graceful Degradation**: Fallback to CPU if GPU fails
- **Error Recovery**: Automatic retry logic
- **Model Fallback**: Use alternative model if one fails
- **Data Integrity**: Checksums for model weights

### 5.4 Security
- **Authentication**: API key support
- **Encryption**: HTTPS/SSL support
- **Input Validation**: Strict input sanitization
- **Rate Limiting**: 100 requests/min per IP
- **CORS**: Configurable cross-origin requests
- **Dependency Management**: Regular security updates

### 5.5 Maintainability
- **Code Quality**: Python best practices
- **Documentation**: Comprehensive API docs
- **Testing**: Unit and integration tests
- **Logging**: Structured logging for debugging
- **Monitoring**: Prometheus metrics export

### 5.6 Usability
- **API Documentation**: Interactive Swagger UI
- **Quick Start**: 5-minute setup guide
- **Error Messages**: Clear, actionable error codes
- **Examples**: Multiple language SDK examples

---

## 6. Success Metrics

### 6.1 Performance Metrics
- Model accuracy (MAE < 8 on test set)
- API response time (p95 < 400ms)
- System availability (>99.5%)
- Prediction confidence (>85% average)

### 6.2 Usage Metrics
- API calls per day
- Average requests per second
- Peak concurrent users
- WebSocket connection duration

### 6.3 Quality Metrics
- Error rate (<0.5%)
- Model drift detection
- Data quality score
- User satisfaction (NPS)

### 6.4 Business Metrics
- User adoption rate
- Feature utilization
- Integration count
- Customer retention

---

## 7. Constraints & Limitations

### 7.1 Technical Constraints
- Requires GPU for optimal performance
- CUDA 12.1+ required for GPU support
- Minimum 6GB VRAM for dual models
- Python 3.8+ required

### 7.2 Model Constraints
- Fixed input resolution (640×480 for CSRNet)
- Training on ShanghaiTech dataset primarily
- May have domain shift on different datasets
- Performance degrades with extremely low light

### 7.3 Infrastructure Constraints
- Single-node deployment max ~20 concurrent requests
- No multi-datacenter failover in base setup
- Limited to publicly available ML models

---

## 8. Timeline & Milestones

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| **Phase 1: MVP** | Completed | Core inference, REST API, Basic UI |
| **Phase 2: Enhancement** | Completed | Training pipeline, WebSocket, Optimization |
| **Phase 3: Production** | In Progress | Security, Monitoring, Documentation |
| **Phase 4: Scale** | Q1 2025 | Multi-GPU, Kubernetes, Advanced Features |
| **Phase 5: Analytics** | Q2 2025 | Dashboard, Reporting, Advanced Analytics |

### Current Status: Phase 3 (Production) ✅

---

## 9. Deployment & Operations

### 9.1 Deployment Options
- Local development (FastAPI development server)
- Docker container (single machine)
- Docker Compose (local multi-container)
- Kubernetes (enterprise/cloud)
- Cloud platforms (AWS ECS, GCP, Azure)

### 9.2 Environment Configurations

#### Development
```bash
DEBUG=true
LOG_LEVEL=DEBUG
GPU_MEMORY_FRACTION=0.5
```

#### Staging
```bash
DEBUG=false
LOG_LEVEL=INFO
GPU_MEMORY_FRACTION=0.7
RATE_LIMIT=100
```

#### Production
```bash
DEBUG=false
LOG_LEVEL=WARNING
GPU_MEMORY_FRACTION=0.8
RATE_LIMIT=100
WORKERS=4
```

---

## 10. Roadmap

### Short Term (Next 3 months)
- [ ] Complete security audit
- [ ] Deploy to production environment
- [ ] Performance optimization (target 10 FPS)
- [ ] Mobile app integration

### Medium Term (3-6 months)
- [ ] Add crowd behavior analysis
- [ ] Implement anomaly detection
- [ ] Enhanced visualization dashboard
- [ ] Analytics/reporting features

### Long Term (6-12 months)
- [ ] Real-time crowd flow prediction
- [ ] Multi-camera tracking
- [ ] Advanced pose estimation
- [ ] Crowd behavior classification

---

## 11. Risk Management

### 11.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Model accuracy degradation on new data | Medium | High | Regular retraining, data validation |
| GPU memory overflow | Low | High | Memory monitoring, fallback to CPU |
| API latency increase under load | Medium | Medium | Load testing, auto-scaling |
| Model weight corruption | Low | High | Checksum verification, backups |

### 11.2 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| User adoption slower than expected | Medium | Medium | Better marketing, free trial |
| Competitor launches similar product | High | Medium | Focus on quality, partnerships |
| Privacy concerns with video | Medium | High | Clear privacy policy, on-premise option |
| Dependency on PyTorch/CUDA | Low | Medium | Regular version updates, vendor monitoring |

---

## 12. Acceptance Criteria

### System Launch Criteria
- [x] All core features implemented
- [x] API documentation complete
- [x] Performance targets met
- [x] Security review passed
- [x] Load testing completed
- [ ] Production deployment
- [ ] User feedback collected
- [ ] Analytics dashboard

### Model Acceptance Criteria
- [x] CSRNet MAE < 8 on validation set
- [x] VMamba accuracy > 85%
- [x] Inference time < 150ms (ensemble)
- [x] Memory usage < 6GB
- [x] Works on diverse scenes

---

## 13. Glossary

| Term | Definition |
|------|-----------|
| **CSRNet** | Congestion Sensing Regression Network - regression-based crowd counting model |
| **VMamba** | Visual State Space Model - state-space model for computer vision |
| **MAE** | Mean Absolute Error - measure of prediction accuracy |
| **Ensemble** | Combination of multiple models for improved predictions |
| **Heatmap** | Density visualization overlaid on image |
| **HLS** | HTTP Live Streaming - adaptive bitrate streaming protocol |
| **CUDA** | Compute Unified Device Architecture - NVIDIA GPU computing platform |
| **FPS** | Frames Per Second - processing speed metric |
| **ASGI** | Asynchronous Server Gateway Interface - web server standard |
| **Inference** | Process of using trained model to make predictions |

---

## 14. Appendix

### 14.1 API Endpoints Reference

**Health Check**
```
GET /health
```

**CSRNet Prediction**
```
POST /api/v1/csrnet/predict
POST /api/v1/csrnet/count
POST /api/v1/csrnet/webcam
```

**VMamba Prediction**
```
POST /api/v1/tmtb/predict
POST /api/v1/tmtb/count
POST /api/v1/tmtb/webcam
```

**Ensemble**
```
POST /api/v1/predict
```

See `docs/API.md` for complete reference.

### 14.2 Configuration Options

```yaml
model:
  csrnet:
    enabled: true
    weights: "/models/csrnet.pth"
    device: "cuda:0"
  tmtb:
    enabled: true
    weights: "/models/tmtb.pth"
    device: "cuda:0"

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

inference:
  batch_size: 1
  mixed_precision: true
  gpu_memory_fraction: 0.8
```

### 14.3 Support & Contact

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Contact**: Team email

---

**Document Approval:**
- Product Manager: _________________
- Technical Lead: _________________
- Project Manager: _________________

**Version History:**
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 2024 | Initial PRD creation |

---

*This document is subject to change based on business needs and technical feasibility.*
