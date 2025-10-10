# ML Architecture Overview

## 📦 **Current ML Structure**

```
ml/
├── src/
│   └── crowd_ml/
│       ├── models/
│       │   ├── csrnet/           # CSRNet implementation
│       │   ├── mcnn/             # MCNN implementation
│       │   ├── tmtb/             # TMTB (VMamba) implementation
│       │   ├── yolo/             # YOLO implementation
│       │   └── vmamba_official.py # Official VMamba code
│       ├── core/                 # Core utilities
│       ├── preprocessing/        # Data preprocessing
│       └── utils/                # Helper functions
├── checkpoints/                  # Model checkpoints
├── datasets/                     # Dataset storage
├── docs/                         # Documentation
└── tests/                        # Unit tests
```

## 🤖 **Implemented Models**

### **CSRNet**

- Density-based crowd counting
- Backend API: `/api/v1/csrnet/predict`
- Health check: `/api/v1/csrnet/health`

### **MCNN**

- Multi-column convolutional network
- Three-column architecture for different scales

### **TMTB (VMamba)**

- State space model for crowd analysis
- Backend API: `/api/v1/tmtb/predict`

### **YOLO**

- Object detection for crowd counting
- Bounding box-based counting approach

## 🔧 **Backend Integration**

### **API Endpoints**

- `POST /api/v1/csrnet/predict` - CSRNet predictions
- `POST /api/v1/tmtb/predict` - TMTB predictions
- Health check endpoints for monitoring

### **Multi-Model Support**

- `predict_multimodel.py` - Handles multiple models
- Unified prediction interface
- Model selection via API parameters

## 📊 **Current Status**

✅ **Implemented:**

- Model architectures (CSRNet, MCNN, TMTB, YOLO)
- Backend API endpoints
- Basic inference pipeline
- Model checkpoints

❌ **Not Yet Implemented:**

- Fine-tuning framework
- Advanced training scripts
- Dataset preprocessing pipeline
- Comprehensive evaluation tools
