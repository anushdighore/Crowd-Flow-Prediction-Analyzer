# 🎯 Quick Reference Guide

## Project Structure At-a-Glance

### Main Directories

| Directory       | Purpose           | Key Contents                  |
| --------------- | ----------------- | ----------------------------- |
| `data/`         | All datasets      | raw/, processed/, external/   |
| `notebooks/`    | Jupyter notebooks | EDA, analysis, prototyping    |
| `src/`          | Source code       | data/, models/, evaluation/   |
| `saved_models/` | Trained models    | base/, checkpoints/, final/   |
| `config/`       | Configuration     | config.yaml, hyperparams.yaml |
| `tests/`        | Unit tests        | test\_\*.py files             |
| `docs/`         | Documentation     | All .md files                 |
| `pipelines/`    | ML pipelines      | Training, inference pipelines |

### Important Files

| File                      | Purpose                    |
| ------------------------- | -------------------------- |
| `README.md`               | Main project documentation |
| `requirements.txt`        | Python dependencies        |
| `setup.py`                | Package installation       |
| `config/config.yaml`      | Main configuration         |
| `config/hyperparams.yaml` | Training hyperparameters   |
| `.gitignore`              | Git ignore rules           |

## Common Commands

### Installation

```bash
# Create environment
conda create -n crowdenv python=3.9
conda activate crowdenv

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Data Preparation

```bash
# Generate density maps
python src/data/create_density_maps.py \
    --dataset data/raw/datasets/ShanghaiTech/ShanghaiTech/part_A \
    --output data/processed/density_maps
```

### Training

```bash
# Train VMamba TMTB
python src/models/train_vmamba.py \
    --checkpoint saved_models/checkpoints/pretrained/jhu_5.pth \
    --data-root data/raw/datasets/ShanghaiTech/ShanghaiTech/part_A \
    --epochs 50 \
    --batch-size 8 \
    --lr 1e-5
```

### Inference

```bash
# Start API server
uvicorn src.models.predict_multimodel:app --host 0.0.0.0 --port 8000

# Or direct prediction
python src/models/predict_multimodel.py --image path/to/image.jpg
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_models.py -v
```

### Update Imports (After Restructuring)

```bash
# Dry run (preview changes)
python scripts/update_imports.py --dry-run

# Apply changes
python scripts/update_imports.py
```

## Import Patterns

### Models

```python
from src.models.architectures.vmamba_tmtb import VMambaTMTB
from src.models.architectures.vmamba_official import load_vmamba_model
from src.models.architectures.csrnet.csrnet import CSRNet
```

### Data Utils

```python
from src.data.utils.preprocess import preprocess_image
from src.data.utils.postprocess import postprocess_density
from src.data.utils.visualize import visualize_results
```

### Preprocessing

```python
from src.data.preprocessing.csrnet_preprocess import CSRNetPreprocessor
```

## Path Patterns

### Data Paths

```python
# Raw data
data_path = "data/raw/datasets/ShanghaiTech/ShanghaiTech/part_A"

# Processed data
processed_path = "data/processed/density_maps"

# External data
external_path = "data/external/custom_dataset"
```

### Model Paths

```python
# Pretrained checkpoint
checkpoint = "saved_models/checkpoints/pretrained/jhu_5.pth"

# Training output
output_dir = "saved_models/checkpoints/run_2024_01_15"

# Final model
final_model = "saved_models/final/vmamba_finetuned_v1"
```

## Configuration Usage

### Load Config

```python
import yaml

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access values
data_root = config['data']['shanghaitech']['part_a']
checkpoint = config['models']['vmamba_tmtb']['checkpoint']
batch_size = config['training']['batch_size']
```

### Load Hyperparameters

```python
import yaml

with open('config/hyperparams.yaml', 'r') as f:
    hyperparams = yaml.safe_load(f)

# Access hyperparameters
lr = hyperparams['vmamba_tmtb']['optimizer']['lr']
epochs = hyperparams['vmamba_tmtb']['epochs']
```

## Troubleshooting

| Issue                 | Solution                               |
| --------------------- | -------------------------------------- |
| `ModuleNotFoundError` | Run `pip install -e .`                 |
| `FileNotFoundError`   | Update paths to new structure          |
| Import errors         | Check import paths match new structure |
| Config not found      | Ensure `config/config.yaml` exists     |
| Old paths in code     | Run `python scripts/update_imports.py` |

## Documentation Quick Links

| Document                                               | Description                  |
| ------------------------------------------------------ | ---------------------------- |
| [README.md](../README.md)                              | Main project documentation   |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)           | Complete structure overview  |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)               | Step-by-step migration guide |
| [RESTRUCTURING_COMPLETE.md](RESTRUCTURING_COMPLETE.md) | Restructuring summary        |
| [QUICKSTART.md](QUICKSTART.md)                         | Quick start guide            |

## Git Workflow

```bash
# After restructuring, commit changes
git add .
git commit -m "Refactor: Reorganize project structure following ML best practices"

# Create a branch for updates
git checkout -b feature/update-imports

# After testing, merge
git checkout main
git merge feature/update-imports
```

## Best Practices

1. ✅ Always use configuration files for paths
2. ✅ Keep raw data immutable (never modify data/raw/)
3. ✅ Use relative imports within src/
4. ✅ Write tests for new features
5. ✅ Document your code
6. ✅ Use version control
7. ✅ Keep checkpoints organized by date/experiment
8. ✅ Update docs when adding features

## Quick Checks

### Verify Installation

```bash
python -c "from src.models.architectures.vmamba_tmtb import VMambaTMTB; print('✅ OK')"
```

### Check Config

```bash
python -c "import yaml; print(yaml.safe_load(open('config/config.yaml'))['project']['name'])"
```

### List Available Models

```bash
ls saved_models/checkpoints/pretrained/
```

### Check Data

```bash
ls data/raw/datasets/
```

## Need Help?

1. Check documentation in `docs/`
2. Review examples in `notebooks/`
3. Check configuration in `config/`
4. Run tests to verify setup: `pytest tests/`
5. Check import paths and file paths

---

**Last Updated:** 2025-01-15
**Version:** 1.0.0
