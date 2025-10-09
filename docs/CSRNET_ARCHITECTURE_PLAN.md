# CSRNet Architecture Plan - GPU-Optimized Multi-Source Inference

## 📋 Overview

This document outlines the plan to restructure CSRNet for:

- **Device Priority**: CUDA Extensions > PyTorch GPU > PyTorch CPU
- **Multi-Source Support**: Static images, videos, webcam, external cameras
- **Real-time Inference**: Optimized for live streaming
- **Fallback Strategy**: Graceful degradation across devices

---

## 🎯 Goals

### Primary Goals

1. ✅ Auto-detect best available device (CUDA ext > GPU > CPU)
2. ✅ Support multiple input sources seamlessly
3. ✅ Optimize for real-time performance
4. ✅ Graceful fallback on device failure
5. ✅ Unified API across all sources

### Performance Targets

- **Static Image**: <0.1s on GPU, <0.5s on CPU
- **Video Processing**: 15-30 FPS on GPU, 5-10 FPS on CPU
- **Webcam (Real-time)**: 20-30 FPS on GPU, 3-5 FPS on CPU
- **External Camera**: Same as webcam

---

## 🏗️ Architecture Components

### 1. Device Manager

**Purpose**: Detect and manage compute devices

**Responsibilities:**

- Detect CUDA extensions (if available)
- Detect PyTorch CUDA (GPU)
- Fallback to PyTorch CPU
- Monitor device health
- Handle device switching

**Priority Order:**

```
1. CUDA Extensions (fastest, if compiled)
   ↓ (if not available)
2. PyTorch CUDA/GPU (fast, native support)
   ↓ (if not available)
3. PyTorch CPU (slower, always available)
```

**Key Methods:**

- `detect_device()` - Auto-detect best device
- `get_device_info()` - Return device capabilities
- `switch_device(target)` - Force device change
- `benchmark_device()` - Test performance

---

### 2. Model Manager

**Purpose**: Load and manage CSRNet model

**Responsibilities:**

- Load checkpoint to detected device
- Handle model state (eval mode)
- Manage model warmup
- Cache loaded models
- Handle model switching

**Features:**

- Lazy loading (load on first inference)
- Model caching (avoid reloading)
- Multi-model support (CSRNet, TMTB, etc.)
- Automatic device placement

**Key Methods:**

- `load_model(model_name, checkpoint_path, device)`
- `get_model(model_name)` - Get cached model
- `warmup_model(model)` - Run warmup inference
- `unload_model(model_name)` - Free memory

---

### 3. Input Source Manager

**Purpose**: Handle different input sources

**Supported Sources:**

1. **Static Images**

   - Single image files (JPG, PNG)
   - Batch processing
   - Directory scanning

2. **Video Files**

   - MP4, AVI, MOV formats
   - Frame extraction
   - Batch processing

3. **Webcam (Built-in)**

   - Real-time streaming
   - Frame buffering
   - FPS control

4. **External Camera**
   - USB cameras
   - IP cameras (RTSP/HTTP)
   - Multiple camera support

**Key Methods:**

- `open_source(source_type, source_path)` - Open input
- `read_frame()` - Get next frame
- `close_source()` - Release resources
- `get_source_info()` - Get metadata

---

### 4. Preprocessing Pipeline

**Purpose**: Standardized image preprocessing

**Responsibilities:**

- Resize/pad if needed (optional)
- ImageNet normalization
- Tensor conversion
- Device placement
- Batch creation

**Features:**

- Source-agnostic preprocessing
- Configurable parameters
- Device-aware tensor creation
- Memory-efficient batching

**Key Methods:**

- `preprocess_image(image, device)` - Single image
- `preprocess_batch(images, device)` - Batch processing
- `preprocess_frame(frame, device)` - Video frame

---

### 5. Inference Engine

**Purpose**: Run model inference

**Responsibilities:**

- Single image inference
- Batch inference
- Streaming inference (real-time)
- Result post-processing
- Performance monitoring

**Features:**

- Automatic batching for efficiency
- FPS limiting for real-time
- Result caching
- Async inference (optional)

**Modes:**

1. **Single Mode**: Process one image
2. **Batch Mode**: Process multiple images
3. **Stream Mode**: Continuous processing
4. **Async Mode**: Non-blocking inference

**Key Methods:**

- `infer_single(image)` - Single inference
- `infer_batch(images)` - Batch inference
- `infer_stream(source)` - Stream processing
- `get_performance_stats()` - Metrics

---

### 6. Output Manager

**Purpose**: Handle inference results

**Responsibilities:**

- Extract crowd count
- Generate density map
- Visualize results
- Save outputs
- Stream results

**Output Formats:**

- **Count**: Integer/float count
- **Density Map**: 2D array/image
- **Visualization**: Overlay on original image
- **JSON**: Structured data for API
- **Video**: Annotated video output

**Key Methods:**

- `get_count(density_map)` - Extract count
- `visualize(image, density_map)` - Create overlay
- `save_result(result, path)` - Save to file
- `format_json(result)` - JSON output

---

## 🔄 Data Flow

### Flow 1: Static Image Processing

```
User provides image path
    ↓
Input Source Manager opens image
    ↓
Preprocessing Pipeline converts to tensor
    ↓
Device Manager determines best device
    ↓
Model Manager loads model to device
    ↓
Inference Engine runs inference
    ↓
Output Manager formats results
    ↓
Return count + density map
```

### Flow 2: Video Processing

```
User provides video path
    ↓
Input Source Manager opens video
    ↓
Loop: For each frame
    ↓
    Preprocessing Pipeline converts frame
    ↓
    Inference Engine runs inference (batched if possible)
    ↓
    Output Manager collects results
    ↓
End Loop
    ↓
Return aggregated results + annotated video
```

### Flow 3: Real-time Webcam

```
User starts webcam
    ↓
Input Source Manager opens webcam stream
    ↓
Device Manager ensures optimal device
    ↓
Model Manager warms up model
    ↓
Loop: While streaming
    ↓
    Read frame from webcam
    ↓
    Preprocessing Pipeline (fast path)
    ↓
    Inference Engine (with FPS limiting)
    ↓
    Output Manager (display + count)
    ↓
End Loop (user stops)
```

### Flow 4: External Camera (IP/USB)

```
User provides camera URL/device ID
    ↓
Input Source Manager connects to camera
    ↓
Same as Webcam flow
```

---

## 🛠️ Component Structure

### Directory Structure

```
ml/src/
├── models/
│   └── csrnet/
│       ├── csrnet.py              # Model architecture
│       ├── device_manager.py       # NEW: Device detection
│       ├── model_manager.py        # NEW: Model loading
│       └── __init__.py
├── inference/
│   ├── engine.py                   # NEW: Inference engine
│   ├── input_sources.py            # NEW: Input handling
│   ├── output_manager.py           # NEW: Output handling
│   └── __init__.py
├── preprocessing/
│   ├── csrnet_preprocess.py        # Existing
│   └── __init__.py
└── utils/
    ├── visualization.py            # NEW: Visualization utils
    ├── metrics.py                  # NEW: Performance tracking
    └── __init__.py
```

---

## 📊 File-by-File Plan

### 1. `models/csrnet/device_manager.py`

**Purpose**: Device detection and management

**Classes:**

- `DeviceManager`

**Key Features:**

- Auto-detect CUDA extensions
- Auto-detect PyTorch GPU
- Fallback to CPU
- Device benchmarking
- Device switching

**Methods:**

```python
class DeviceManager:
    def __init__(self):
        self.available_devices = []
        self.current_device = None
        self.device_info = {}

    def detect_devices(self) -> List[str]:
        """Detect all available devices"""
        pass

    def get_best_device(self) -> str:
        """Get best available device"""
        pass

    def benchmark_device(self, device: str) -> Dict:
        """Benchmark device performance"""
        pass

    def set_device(self, device: str):
        """Set current device"""
        pass

    def get_device_info(self, device: str) -> Dict:
        """Get device specifications"""
        pass
```

---

### 2. `models/csrnet/model_manager.py`

**Purpose**: Model loading and caching

**Classes:**

- `ModelManager`

**Key Features:**

- Lazy loading
- Model caching
- Multi-model support
- Device placement
- Warmup

**Methods:**

```python
class ModelManager:
    def __init__(self, device_manager: DeviceManager):
        self.models = {}
        self.device_manager = device_manager

    def load_model(self, model_name: str, checkpoint: str, device: str):
        """Load model to device"""
        pass

    def get_model(self, model_name: str):
        """Get cached model"""
        pass

    def warmup_model(self, model_name: str):
        """Warmup model with dummy input"""
        pass

    def unload_model(self, model_name: str):
        """Unload model from memory"""
        pass

    def switch_device(self, model_name: str, new_device: str):
        """Move model to different device"""
        pass
```

---

### 3. `inference/input_sources.py`

**Purpose**: Handle different input sources

**Classes:**

- `InputSource` (base class)
- `ImageSource`
- `VideoSource`
- `WebcamSource`
- `ExternalCameraSource`

**Key Features:**

- Unified interface
- Source metadata
- Frame buffering
- Auto-reconnect (for streams)

**Methods:**

```python
class InputSource:
    def open(self, source_path: str):
        """Open source"""
        pass

    def read_frame(self) -> np.ndarray:
        """Read next frame"""
        pass

    def close(self):
        """Close source"""
        pass

    def get_info(self) -> Dict:
        """Get source metadata"""
        pass

    def is_open(self) -> bool:
        """Check if source is open"""
        pass
```

---

### 4. `inference/engine.py`

**Purpose**: Inference execution

**Classes:**

- `InferenceEngine`

**Key Features:**

- Multiple inference modes
- Batching support
- Performance tracking
- Async support (optional)

**Methods:**

```python
class InferenceEngine:
    def __init__(self, model_manager: ModelManager, device_manager: DeviceManager):
        self.model_manager = model_manager
        self.device_manager = device_manager
        self.stats = {}

    def infer_single(self, image: np.ndarray, model_name: str) -> Dict:
        """Single image inference"""
        pass

    def infer_batch(self, images: List[np.ndarray], model_name: str) -> List[Dict]:
        """Batch inference"""
        pass

    def infer_stream(self, source: InputSource, model_name: str, callback=None):
        """Stream inference"""
        pass

    def get_stats(self) -> Dict:
        """Get performance statistics"""
        pass
```

---

### 5. `inference/output_manager.py`

**Purpose**: Format and save results

**Classes:**

- `OutputManager`

**Key Features:**

- Multiple output formats
- Visualization
- Streaming output
- Result caching

**Methods:**

```python
class OutputManager:
    def __init__(self):
        self.cache = {}

    def format_result(self, density_map, format: str) -> Any:
        """Format result (json/image/video)"""
        pass

    def visualize(self, image: np.ndarray, density_map: np.ndarray) -> np.ndarray:
        """Create visualization overlay"""
        pass

    def save_result(self, result: Dict, path: str):
        """Save result to file"""
        pass

    def stream_result(self, result: Dict, stream_handler):
        """Stream result (for real-time)"""
        pass
```

---

### 6. `utils/visualization.py`

**Purpose**: Visualization utilities

**Functions:**

- `overlay_density_map(image, density_map, alpha=0.5)`
- `draw_count(image, count, position)`
- `create_heatmap(density_map, colormap='jet')`
- `annotate_video(video_path, results, output_path)`

---

### 7. `utils/metrics.py`

**Purpose**: Performance tracking

**Classes:**

- `PerformanceTracker`

**Features:**

- FPS tracking
- Latency measurement
- Device utilization
- Memory usage

---

## 🎨 API Design

### High-Level API (Simple)

```python
from models.csrnet import CSRNetInference

# Initialize (auto-detects best device)
csrnet = CSRNetInference(
    checkpoint_path='checkpoints/csrnet.pth',
    auto_device=True
)

# Single image
result = csrnet.predict_image('crowd.jpg')
print(f"Count: {result['count']}")

# Video
results = csrnet.predict_video('crowd_video.mp4', save_output=True)

# Webcam (real-time)
csrnet.predict_webcam(display=True, save_output=False)

# External camera
csrnet.predict_camera('rtsp://camera-url', display=True)
```

### Low-Level API (Advanced)

```python
from models.csrnet import DeviceManager, ModelManager, InferenceEngine
from inference import ImageSource, OutputManager

# Manual control
device_mgr = DeviceManager()
device = device_mgr.get_best_device()

model_mgr = ModelManager(device_mgr)
model_mgr.load_model('csrnet', 'checkpoints/csrnet.pth', device)

engine = InferenceEngine(model_mgr, device_mgr)

# Custom inference
source = ImageSource('crowd.jpg')
result = engine.infer_single(source.read_frame(), 'csrnet')
```

---

## 📈 Performance Optimization Strategies

### 1. Device Level

- [x] Auto-select fastest device
- [ ] Mixed precision (FP16) on GPU
- [ ] TensorRT optimization (advanced)
- [ ] ONNX export (optional)

### 2. Inference Level

- [ ] Batch processing for videos
- [ ] Frame skipping for real-time
- [ ] Result caching
- [ ] Async inference queue

### 3. Memory Level

- [ ] Model quantization
- [ ] Gradient checkpointing
- [ ] Memory pooling
- [ ] Lazy loading

---

## 🧪 Testing Strategy

### Unit Tests

- [ ] Device detection
- [ ] Model loading
- [ ] Input sources
- [ ] Preprocessing
- [ ] Inference engine
- [ ] Output formatting

### Integration Tests

- [ ] End-to-end image processing
- [ ] End-to-end video processing
- [ ] Real-time webcam
- [ ] Device fallback

### Performance Tests

- [ ] Benchmark all devices
- [ ] FPS measurement
- [ ] Memory profiling
- [ ] Latency testing

---

## 📝 Configuration

### Config File: `config/csrnet_config.yaml`

```yaml
device:
  auto_detect: true
  preferred: "cuda" # cuda, cpu, auto
  fallback: true
  benchmark_on_init: false

model:
  checkpoint: "checkpoints/csrnet.pth"
  warmup: true
  cache_models: true

inference:
  batch_size: 4
  precision: "fp32" # fp32, fp16
  async: false

realtime:
  target_fps: 30
  max_fps: 60
  buffer_size: 2
  skip_frames: false

output:
  format: "json" # json, image, video
  visualize: true
  save_results: false
  overlay_alpha: 0.5
```

---

## 🚀 Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Priority: HIGH**

- [x] Create directory structure
- [ ] Implement DeviceManager
- [ ] Implement ModelManager
- [ ] Write unit tests
- [ ] Documentation

**Deliverable**: Working device detection and model loading

---

### Phase 2: Input Handling (Week 1-2)

**Priority: HIGH**

- [ ] Implement InputSource classes
- [ ] Image source
- [ ] Video source
- [ ] Webcam source
- [ ] External camera source
- [ ] Write tests

**Deliverable**: All input sources working

---

### Phase 3: Inference Engine (Week 2)

**Priority: HIGH**

- [ ] Implement InferenceEngine
- [ ] Single inference mode
- [ ] Batch inference mode
- [ ] Stream inference mode
- [ ] Performance tracking
- [ ] Write tests

**Deliverable**: Working inference on all sources

---

### Phase 4: Output & Visualization (Week 2-3)

**Priority: MEDIUM**

- [ ] Implement OutputManager
- [ ] Visualization utilities
- [ ] Result formatting
- [ ] Video annotation
- [ ] Write tests

**Deliverable**: Complete output pipeline

---

### Phase 5: High-Level API (Week 3)

**Priority: MEDIUM**

- [ ] Create unified CSRNetInference class
- [ ] Simple API methods
- [ ] Configuration loading
- [ ] Error handling
- [ ] Documentation

**Deliverable**: User-friendly API

---

### Phase 6: Optimization (Week 3-4)

**Priority: LOW**

- [ ] FP16 support
- [ ] Batching optimization
- [ ] Memory optimization
- [ ] Async inference
- [ ] Benchmarking

**Deliverable**: Optimized performance

---

### Phase 7: Testing & Documentation (Week 4)

**Priority: HIGH**

- [ ] Complete test suite
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] User documentation
- [ ] API documentation

**Deliverable**: Production-ready system

---

## 🎯 Success Criteria

### Functional Requirements

- ✅ Auto-detects GPU and uses it if available
- ✅ Falls back to CPU gracefully
- ✅ Processes static images
- ✅ Processes videos
- ✅ Real-time webcam inference
- ✅ External camera support
- ✅ Unified API

### Performance Requirements

- ✅ GPU inference: <0.1s per image
- ✅ CPU inference: <0.5s per image
- ✅ Real-time: 20+ FPS on GPU
- ✅ Memory efficient (<2GB VRAM)

### Quality Requirements

- ✅ 95%+ test coverage
- ✅ Complete documentation
- ✅ Error handling
- ✅ Logging and monitoring

---

## 📚 Dependencies

### Required

- `torch >= 2.0.0`
- `torchvision >= 0.15.0`
- `opencv-python >= 4.8.0`
- `numpy >= 1.24.0`
- `pillow >= 10.0.0`

### Optional

- `tensorrt` (for TRT optimization)
- `onnx` (for ONNX export)
- `streamlit` (for web UI)

---

## 🔧 Backward Compatibility

### Existing Code

- Keep existing `load_csrnet()` function
- Keep existing preprocessing
- Add deprecation warnings
- Provide migration guide

### Migration Path

```python
# Old way (still works)
from models.csrnet.csrnet import load_csrnet
model = load_csrnet('checkpoint.pth', device='cpu')

# New way (recommended)
from models.csrnet import CSRNetInference
csrnet = CSRNetInference('checkpoint.pth')
result = csrnet.predict_image('image.jpg')
```

---

## 📊 Monitoring & Metrics

### Real-time Metrics

- FPS (frames per second)
- Latency (inference time)
- Device utilization
- Memory usage
- Queue length

### Aggregate Metrics

- Total frames processed
- Average FPS
- Error rate
- Uptime

---

## 🐛 Error Handling

### Device Errors

- GPU out of memory → Fallback to CPU
- CUDA error → Fallback to CPU
- Device not available → Use CPU

### Input Errors

- Invalid image → Skip and log
- Camera disconnected → Retry connection
- Video corrupted → Skip frame

### Model Errors

- Checkpoint not found → Clear error message
- Architecture mismatch → Validation error
- Inference failure → Fallback mode

---

## 📖 Documentation Plan

### 1. Architecture Documentation

- Component diagrams
- Data flow diagrams
- API documentation
- Configuration guide

### 2. User Guides

- Quick start guide
- Image processing tutorial
- Video processing tutorial
- Real-time webcam tutorial
- External camera setup

### 3. Developer Guides

- Contributing guide
- Testing guide
- Performance tuning
- Troubleshooting

---

## ✅ Next Steps

1. **Review this plan** - Get feedback on architecture
2. **Create flowchart** - Visual representation (separate doc)
3. **Start Phase 1** - Implement core infrastructure
4. **Iterate** - Build, test, refine

---

## 📝 Notes

- This plan prioritizes GPU utilization while maintaining CPU fallback
- Real-time performance is key for webcam/camera sources
- Modular design allows easy extension to other models (TMTB, MCNN)
- Focus on production-ready code with proper error handling

---

**Status**: 📋 PLAN PHASE
**Next**: Create visual flowchart in `docs/csrnet-structure.md`
**Timeline**: 4 weeks to full implementation
**Priority**: Device management and input handling first
