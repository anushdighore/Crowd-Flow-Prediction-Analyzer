# ML Folder Structure - Long-term Architecture

## 📦 **Complete ML Directory Structure**

```
ml/
├── src/
│   └── crowd_ml/                          # Main installable package
│       ├── __init__.py
│       ├── __version__.py                 # Version tracking
│       │
│       ├── models/                        # Model architectures
│       │   ├── __init__.py
│       │   ├── base.py                    # Abstract base model
│       │   ├── csrnet/
│       │   │   ├── __init__.py
│       │   │   ├── architecture.py        # CSRNet architecture
│       │   │   └── loader.py              # Model loading logic
│       │   ├── vmamba/
│       │   │   ├── __init__.py
│       │   │   ├── architecture.py
│       │   │   └── loader.py
│       │   ├── mcnn/
│       │   │   ├── __init__.py
│       │   │   ├── architecture.py
│       │   │   └── loader.py
│       │   └── factory.py                 # Model factory pattern
│       │
│       ├── inference/                     # Inference engine
│       │   ├── __init__.py
│       │   ├── predictor.py               # Main predictor class
│       │   ├── batch.py                   # Batch inference
│       │   └── streaming.py               # Streaming/real-time inference
│       │
│       ├── preprocessing/                 # Data preprocessing
│       │   ├── __init__.py
│       │   ├── transforms.py              # Image transforms
│       │   ├── augmentations.py           # Data augmentation
│       │   └── normalization.py           # Normalization utils
│       │
│       ├── postprocessing/                # Output processing
│       │   ├── __init__.py
│       │   ├── density_to_count.py        # Density map → count
│       │   └── heatmap.py                 # Heatmap generation
│       │
│       ├── data/                          # Data handling
│       │   ├── __init__.py
│       │   ├── datasets.py                # PyTorch datasets
│       │   ├── loaders.py                 # Data loaders
│       │   └── samplers.py                # Custom samplers
│       │
│       ├── training/                      # Training logic
│       │   ├── __init__.py
│       │   ├── trainer.py                 # Main trainer class
│       │   ├── losses.py                  # Loss functions
│       │   ├── metrics.py                 # Evaluation metrics
│       │   └── callbacks.py               # Training callbacks
│       │
│       ├── evaluation/                    # Model evaluation
│       │   ├── __init__.py
│       │   ├── evaluator.py               # Evaluation pipeline
│       │   └── benchmarks.py              # Benchmark utils
│       │
│       └── utils/                         # Utilities
│           ├── __init__.py
│           ├── logging.py                 # Logging setup
│           ├── visualization.py           # Plotting utils
│           ├── checkpoint.py              # Checkpoint management
│           └── device.py                  # Device management (CPU/GPU)
│
├── checkpoints/                           # Model weights
│   ├── csrnet/
│   │   ├── csrnet_sha.pth                # ShanghaiTech A
│   │   ├── csrnet_shb.pth                # ShanghaiTech B
│   │   └── metadata.json                 # Model metadata
│   ├── vmamba/
│   │   ├── vmamba_tmtb.pth
│   │   └── metadata.json
│   └── README.md
│
├── configs/                               # Configuration files
│   ├── models/
│   │   ├── csrnet.yaml                   # CSRNet config
│   │   ├── vmamba.yaml                   # VMamba config
│   │   └── mcnn.yaml                     # MCNN config
│   ├── training/
│   │   ├── default.yaml                  # Default training config
│   │   └── distributed.yaml              # Multi-GPU training
│   └── inference/
│       ├── fast.yaml                     # Fast inference
│       └── accurate.yaml                 # Accurate inference
│
├── data/                                  # Training/evaluation data
│   ├── raw/                              # Original datasets
│   │   ├── ShanghaiTech/
│   │   ├── UCF_CC_50/
│   │   └── JHU_CROWD/
│   ├── processed/                        # Preprocessed data
│   │   ├── density_maps/
│   │   └── annotations/
│   ├── splits/                           # Train/val/test splits
│   │   ├── train.txt
│   │   ├── val.txt
│   │   └── test.txt
│   └── README.md
│
├── experiments/                           # Experiment tracking
│   ├── exp_001_csrnet_baseline/
│   │   ├── config.yaml                   # Experiment config
│   │   ├── metrics.json                  # Results
│   │   ├── checkpoints/                  # Best models
│   │   └── logs/                         # Training logs
│   ├── exp_002_vmamba_finetuned/
│   └── README.md
│
├── notebooks/                             # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_analysis.ipynb
│   ├── 03_inference_testing.ipynb
│   └── README.md
│
├── scripts/                               # Standalone scripts
│   ├── train.py                          # Training script
│   ├── evaluate.py                       # Evaluation script
│   ├── inference.py                      # Batch inference
│   ├── export_onnx.py                    # Model export
│   ├── download_data.py                  # Data download
│   └── preprocess_dataset.py             # Data preprocessing
│
├── tests/                                 # Unit tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_inference.py
│   ├── test_preprocessing.py
│   └── conftest.py
│
├── docs/                                  # Documentation
│   ├── api/                              # API docs
│   ├── models/                           # Model documentation
│   └── tutorials/                        # Tutorials
│
├── docker/                                # Docker configs
│   ├── Dockerfile.train                  # Training container
│   ├── Dockerfile.inference              # Inference container
│   └── docker-compose.yml
│
├── .gitignore
├── pyproject.toml                         # Package definition
├── setup.py                              # Setup script (legacy)
├── requirements.txt                       # Dependencies
├── requirements-dev.txt                   # Dev dependencies
├── README.md                             # Main documentation
└── CHANGELOG.md                          # Version history
```

---

## 🎯 **Key Design Principles**

### 1. **Installable Package** (`src/crowd_ml/`)

- Clean separation of library code
- Can be installed with: `pip install -e .`
- Reusable across projects
- Proper import paths: `from crowd_ml.models import CSRNet`

### 2. **Separation of Concerns**

- **Models**: Architecture definitions only
- **Inference**: Business logic for predictions
- **Training**: Training logic separate from models
- **Data**: Data handling separate from models

### 3. **Configuration Management**

- YAML configs for reproducibility
- Separate configs for models, training, inference
- Easy to swap configurations

### 4. **Experiment Tracking**

- Each experiment in its own folder
- Stores config, metrics, checkpoints, logs
- Easy to compare experiments

### 5. **Scalability**

- Batch inference support
- Distributed training ready
- Model export (ONNX) support

---

## 📋 **Folder Descriptions**

### **`src/crowd_ml/`** - The Core Package

| **Module**        | **Purpose**         | **Example**                                   |
| ----------------- | ------------------- | --------------------------------------------- |
| `models/`         | Model architectures | `from crowd_ml.models import CSRNet`          |
| `inference/`      | Prediction logic    | `predictor = Predictor.from_checkpoint(path)` |
| `preprocessing/`  | Input transforms    | `transform = get_inference_transform()`       |
| `postprocessing/` | Output processing   | `count = density_to_count(density_map)`       |
| `training/`       | Training pipeline   | `trainer = Trainer(model, config)`            |
| `evaluation/`     | Evaluation metrics  | `evaluator = Evaluator(model, dataset)`       |
| `utils/`          | Helper functions    | Various utilities                             |

### **`checkpoints/`** - Model Weights

```
checkpoints/
├── csrnet/
│   ├── csrnet_sha.pth          # 145 MB
│   └── metadata.json           # {date, metrics, config}
└── vmamba/
    ├── vmamba_tmtb.pth         # 350 MB
    └── metadata.json
```

### **`configs/`** - YAML Configurations

```yaml
# configs/models/csrnet.yaml
model:
  name: csrnet
  architecture:
    frontend: vgg16
    backend: dilated_conv

inference:
  device: cuda
  batch_size: 1

preprocessing:
  input_size: [512, 512]
  normalize: true
```

### **`experiments/`** - Experiment Tracking

```
experiments/
├── exp_001_csrnet_baseline/
│   ├── config.yaml              # Full config snapshot
│   ├── metrics.json             # MAE, MSE, etc.
│   ├── checkpoints/
│   │   ├── best.pth
│   │   └── last.pth
│   └── logs/
│       └── training.log
```

### **`scripts/`** - CLI Tools

```bash
# Training
python scripts/train.py --config configs/training/default.yaml

# Evaluation
python scripts/evaluate.py --checkpoint checkpoints/csrnet/best.pth

# Inference
python scripts/inference.py --input image.jpg --model csrnet
```

---

## 💻 **Usage Examples**

### **1. Install the Package**

```bash
cd ml/
pip install -e .  # Installs crowd_ml in editable mode
```

### **2. Use in Backend**

```python
# backend/app/api/endpoints/csrnet.py
from crowd_ml.inference import Predictor
from crowd_ml.models import CSRNet

# Load model
predictor = Predictor.from_checkpoint(
    model_class=CSRNet,
    checkpoint_path="ml/checkpoints/csrnet/csrnet_sha.pth",
    device="cuda"
)

# Predict
result = predictor.predict(image_bytes)
print(result['count'], result['density_map'])
```

### **3. Training Script**

```python
# scripts/train.py
from crowd_ml.models import CSRNet
from crowd_ml.training import Trainer
from crowd_ml.data import CrowdDataset

model = CSRNet()
dataset = CrowdDataset("data/processed/")
trainer = Trainer(model, dataset)
trainer.train(epochs=100)
```

### **4. Notebook Analysis**

```python
# notebooks/model_analysis.ipynb
from crowd_ml.models import CSRNet
from crowd_ml.evaluation import Evaluator

model = CSRNet.from_checkpoint("checkpoints/csrnet/best.pth")
evaluator = Evaluator(model)
metrics = evaluator.evaluate(test_dataset)
evaluator.plot_results()
```

---

## 🚀 **Benefits of This Structure**

✅ **Clean Separation**: Models, training, inference all separate  
✅ **Reusable**: Can use crowd_ml in any project  
✅ **Scalable**: Easy to add new models/features  
✅ **Testable**: Clear test organization  
✅ **Reproducible**: Config-driven, experiment tracking  
✅ **Production-Ready**: Docker, ONNX export, API-ready  
✅ **Maintainable**: Clear structure, easy to navigate

---

## 📝 **Migration Path**

To move from current structure to this:

1. Create `src/crowd_ml/` package structure
2. Move model architectures to `src/crowd_ml/models/`
3. Move utilities to respective packages
4. Create `pyproject.toml` for installation
5. Update imports in backend
6. Test everything works

Would you like me to start implementing this structure? 🚀
