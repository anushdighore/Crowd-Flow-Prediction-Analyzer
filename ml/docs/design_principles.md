# Design Principles

## 🎯 **Core Architecture Decisions**

### **Modular Model Design**

- Each model (CSRNet, MCNN, TMTB, YOLO) in separate directory
- Independent implementation and loading
- Consistent interface across models

### **Backend-First Approach**

- REST API endpoints for all models
- File upload support for predictions
- Health check endpoints for monitoring

### **Multi-Model Support**

- Unified prediction interface
- Model selection via API parameters
- Consistent response format

## 📁 **Directory Organization**

### **Models Directory**

```
models/
├── csrnet/           # CSRNet specific code
├── mcnn/             # MCNN specific code
├── tmtb/             # TMTB specific code
├── yolo/             # YOLO specific code
└── vmamba_official.py # Official VMamba implementation
```

### **Backend Integration**

```
backend/app/
├── api/v1/endpoints/
│   ├── csrnet.py     # CSRNet API
│   └── tmtb.py       # TMTB API
└── predict_multimodel.py # Multi-model handler
```

## 🔧 **Current Implementation Status**

### **What's Working**

- ✅ Model loading and basic inference
- ✅ API endpoints for CSRNet and TMTB
- ✅ File upload and prediction response
- ✅ Health check monitoring

### **Architecture Principles**

- **Separation of Concerns**: Models, backend, and frontend are independent
- **Consistent Interfaces**: All models follow same prediction API
- **Scalability**: Easy to add new models following existing patterns
- **Maintainability**: Clear directory structure and modular code
