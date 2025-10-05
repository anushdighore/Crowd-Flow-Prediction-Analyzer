# Project Structure Documentation

## 📁 Complete Directory Tree

```
Crowd-Flow-Prediction-Analyzer/
│
├── 📊 data/                           # All data files
│   ├── raw/                           # Original, immutable data
│   │   └── datasets/                  # Raw datasets
│   │       └── ShanghaiTech/
│   │           ├── part_A/
│   │           │   ├── train_data/
│   │           │   │   ├── images/
│   │           │   │   └── ground-truth/
│   │           │   └── test_data/
│   │           │       ├── images/
│   │           │       └── ground-truth/
│   │           └── part_B/
│   │
│   ├── processed/                     # Cleaned and transformed data
│   │   ├── density_maps/
│   │   ├── augmented/
│   │   └── features/
│   │
│   └── external/                      # External datasets
│       └── additional_datasets/
│
├── 📓 notebooks/                      # Jupyter notebooks
│   ├── dataset_preparation.ipynb      # Data preparation workflow
│   ├── model_exploration.ipynb        # Model architecture exploration
│   ├── results_analysis.ipynb         # Results analysis
│   └── visualization.ipynb            # Visualization examples
│
├── 🔧 src/                            # Source code
│   ├── __init__.py
│   │
│   ├── 📥 data/                       # Data processing
│   │   ├── __init__.py
│   │   ├── create_density_maps.py     # Generate density maps from annotations
│   │   ├── make_dataset.py            # Dataset creation scripts
│   │   ├── build_features.py          # Feature engineering
│   │   │
│   │   ├── utils/                     # Data utilities
│   │   │   ├── __init__.py
│   │   │   ├── preprocess.py          # Image preprocessing
│   │   │   ├── postprocess.py         # Post-processing utilities
│   │   │   ├── visualize.py           # Visualization tools
│   │   │   ├── webcam.py              # Webcam utilities
│   │   │   └── csrnet/
│   │   │       ├── csrnet.py
│   │   │       └── diagnose_checkpoint.py
│   │   │
│   │   └── preprocessing/             # Preprocessing modules
│   │       ├── __init__.py
│   │       ├── csrnet_preprocess.py
│   │       ├── README.md
│   │       └── QUICK_REFERENCE.md
│   │
│   ├── 🤖 models/                     # Model training & prediction
│   │   ├── __init__.py
│   │   ├── train_vmamba.py            # VMamba training script
│   │   ├── predict_multimodel.py      # Multi-model inference API
│   │   │
│   │   └── architectures/             # Model definitions
│   │       ├── __init__.py
│   │       ├── model_factory.py       # Model factory pattern
│   │       ├── vmamba_tmtb.py         # VMamba-TMTB architecture
│   │       ├── vmamba_official.py     # Official VMamba implementation
│   │       ├── mcnn.py                # Multi-column CNN
│   │       ├── yolov8_counter.py      # YOLOv8-based counter
│   │       │
│   │       ├── csrnet/                # CSRNet module
│   │       │   ├── __init__.py
│   │       │   ├── csrnet.py
│   │       │   └── api.py
│   │       │
│   │       └── official/              # Official implementations
│   │           ├── vmamba.py
│   │           ├── model.py
│   │           ├── counting_head.py
│   │           ├── csms6s.py
│   │           └── csm_triton.py
│   │
│   └── 📈 evaluation/                 # Evaluation & metrics
│       ├── __init__.py
│       ├── evaluate_model.py          # Model evaluation script
│       ├── metrics.py                 # Custom metrics
│       └── visualization.py           # Result visualization
│
├── 💾 saved_models/                   # Trained models
│   ├── base/                          # Pretrained base models
│   │   └── (downloaded from HuggingFace/external)
│   │
│   ├── checkpoints/                   # Training checkpoints
│   │   ├── pretrained/                # Pretrained weights
│   │   │   ├── jhu_5.pth              # VMamba pretrained on JHU
│   │   │   └── csrnet.pth             # CSRNet pretrained
│   │   │
│   │   └── run_2024-XX-XX_XXXX/       # Training run checkpoints
│   │       ├── checkpoint-1000/
│   │       ├── checkpoint-2000/
│   │       └── trainer_state.json
│   │
│   └── final/                         # Final exported models
│       └── vmamba-finetuned-v1/
│           ├── config.json
│           ├── pytorch_model.bin
│           ├── model_card.md
│           └── README.md
│
├── ⚙️ config/                         # Configuration files
│   ├── config.yaml                    # Main configuration
│   ├── hyperparams.yaml               # Hyperparameters
│   └── logging.yaml                   # Logging configuration
│
├── 🧪 tests/                          # Unit & integration tests
│   ├── __init__.py
│   ├── test_data.py                   # Data loading tests
│   ├── test_models.py                 # Model tests
│   ├── test_preprocessing.py          # Preprocessing tests
│   └── test_api.py                    # API endpoint tests
│
├── 📚 docs/                           # Documentation
│   ├── README.md                      # Main documentation index
│   ├── MIGRATION_GUIDE.md             # Migration guide from old structure
│   ├── QUICKSTART.md                  # Quick start guide
│   ├── QUICKSTART_VMAMBA.md           # VMamba specific guide
│   ├── QUICKSTART_MULTIMODEL.md       # Multi-model guide
│   ├── API_REFERENCE.md               # API documentation
│   ├── DATASET_PREPARATION.md         # Dataset setup guide
│   ├── MODEL_COMPARISON.md            # Model comparison
│   ├── INSTALLATION_PRIORITY.md       # Installation guide
│   ├── SYSTEM_DIAGRAMS.md             # Architecture diagrams
│   ├── PROJECT_SUMMARY.md             # Project overview
│   ├── VMAMBA_FINETUNING_SUMMARY.md   # Fine-tuning guide
│   └── model_card.md                  # Model card template
│
├── 🔄 pipelines/                      # ML pipeline orchestration
│   ├── __init__.py
│   ├── training_pipeline.py           # Training pipeline
│   ├── inference_pipeline.py          # Inference pipeline
│   └── data_pipeline.py               # Data processing pipeline
│
├── 🌐 crowd-counter-frontend/         # React frontend (separate module)
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── README.md
│
├── 📋 app/                            # Legacy application files
│   └── main.py                        # FastAPI main app
│
├── 📄 Root Files
├── .gitignore                         # Git ignore rules
├── .env.example                       # Environment variables template
├── README.md                          # Project README
├── requirements.txt                   # Python dependencies
├── setup.py                           # Package setup
├── pyproject.toml                     # Modern Python project config
├── LICENSE                            # License file
└── CONTRIBUTING.md                    # Contribution guidelines
```

## 📊 Directory Purpose

### `/data`

- **Purpose**: All data files and datasets
- **Subdirectories**:
  - `raw/`: Original, immutable datasets (never modify these)
  - `processed/`: Cleaned, transformed data ready for training
  - `external/`: External or third-party datasets

### `/notebooks`

- **Purpose**: Exploratory analysis, prototyping, visualization
- **Contents**: Jupyter notebooks for experimentation
- **Usage**: Interactive development, results analysis

### `/src`

- **Purpose**: All production source code
- **Subdirectories**:
  - `data/`: Data loading, preprocessing, feature engineering
  - `models/`: Model architectures, training, prediction
  - `evaluation/`: Metrics, validation, evaluation scripts

### `/saved_models`

- **Purpose**: Store trained models and checkpoints
- **Subdirectories**:
  - `base/`: Pretrained models from external sources
  - `checkpoints/`: Intermediate training checkpoints
  - `final/`: Production-ready exported models

### `/config`

- **Purpose**: Configuration management
- **Contents**: YAML/JSON config files for reproducibility
- **Usage**: Centralized configuration for experiments

### `/tests`

- **Purpose**: Unit and integration tests
- **Framework**: pytest
- **Coverage**: Data, models, preprocessing, API

### `/docs`

- **Purpose**: Project documentation
- **Contents**: Guides, API docs, architecture diagrams
- **Format**: Markdown files

### `/pipelines`

- **Purpose**: ML pipeline orchestration
- **Contents**: Training, inference, data processing pipelines
- **Tools**: Can integrate with Airflow, Kubeflow, MLflow, etc.

## 🔄 Data Flow

```
Raw Data (data/raw/)
    ↓
Preprocessing (src/data/)
    ↓
Processed Data (data/processed/)
    ↓
Training (src/models/train_*.py)
    ↓
Checkpoints (saved_models/checkpoints/)
    ↓
Evaluation (src/evaluation/)
    ↓
Final Model (saved_models/final/)
    ↓
Inference (src/models/predict_*.py)
    ↓
Results
```

## 🎯 Key Principles

1. **Separation of Concerns**: Data, models, and evaluation are separate
2. **Reproducibility**: Config files for all experiments
3. **Modularity**: Each component is independent and reusable
4. **Testability**: Comprehensive test coverage
5. **Documentation**: Well-documented code and processes
6. **Scalability**: Structure supports growth and collaboration

## 📝 File Naming Conventions

- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Config files**: `lowercase.yaml`
- **Notebooks**: `descriptive_name.ipynb`
- **Tests**: `test_*.py`
- **Documentation**: `UPPERCASE.md` for important docs

## 🚀 Getting Started

1. **Data Preparation**: Start in `/notebooks/dataset_preparation.ipynb`
2. **Training**: Use scripts in `/src/models/`
3. **Evaluation**: Run `/src/evaluation/evaluate_model.py`
4. **Deployment**: Use models from `/saved_models/final/`

## 📖 Further Reading

- [Migration Guide](MIGRATION_GUIDE.md) - How to update old code
- [Quick Start](QUICKSTART.md) - Get up and running quickly
- [API Reference](API_REFERENCE.md) - API documentation
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines

---

This structure follows industry best practices and is designed for:

- ✅ Collaboration
- ✅ Reproducibility
- ✅ Scalability
- ✅ Maintainability
- ✅ Production deployment
