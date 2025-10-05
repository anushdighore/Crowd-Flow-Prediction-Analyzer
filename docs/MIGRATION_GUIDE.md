# Project Structure Migration Guide

This document provides guidance on updating import statements and file paths after the project restructuring.

## Directory Structure Changes

### Old → New Structure

```
Old Structure:
├── models/              → src/models/architectures/
├── utils/               → src/data/utils/
├── preprocessing/       → src/data/preprocessing/
├── datasets/            → data/raw/datasets/
├── checkpoints/         → saved_models/checkpoints/pretrained/
├── *.md files           → docs/
├── Untitled.ipynb       → notebooks/dataset_preparation.ipynb
├── test_*.py            → tests/
└── finetune_vmamba.py   → src/models/train_vmamba.py
```

## Import Statement Updates

### 1. Model Imports

**Old:**

```python
from models.vmamba_tmtb import VMambaTMTB, load_vmamba_tmtb
from models.vmamba_official import load_vmamba_model
from models.csrnet.csrnet import CSRNet
```

**New:**

```python
from src.models.architectures.vmamba_tmtb import VMambaTMTB, load_vmamba_tmtb
from src.models.architectures.vmamba_official import load_vmamba_model
from src.models.architectures.csrnet.csrnet import CSRNet
```

### 2. Utilities Imports

**Old:**

```python
from utils.preprocess import preprocess_image
from utils.postprocess import postprocess_density
from utils.visualize import visualize_results
```

**New:**

```python
from src.data.utils.preprocess import preprocess_image
from src.data.utils.postprocess import postprocess_density
from src.data.utils.visualize import visualize_results
```

### 3. Preprocessing Imports

**Old:**

```python
from preprocessing.csrnet_preprocess import CSRNetPreprocessor
```

**New:**

```python
from src.data.preprocessing.csrnet_preprocess import CSRNetPreprocessor
```

## File Path Updates

### 1. Dataset Paths

**Old:**

```python
data_root = "datasets/ShanghaiTech/ShanghaiTech/part_A"
```

**New:**

```python
data_root = "data/raw/datasets/ShanghaiTech/ShanghaiTech/part_A"
```

### 2. Checkpoint Paths

**Old:**

```python
checkpoint_path = "checkpoints/jhu_5.pth"
```

**New:**

```python
checkpoint_path = "saved_models/checkpoints/pretrained/jhu_5.pth"
```

### 3. Output Paths

**Old:**

```python
output_dir = "outputs/"
```

**New:**

```python
output_dir = "saved_models/final/"
# or for intermediate results
output_dir = "saved_models/checkpoints/run_name/"
```

## Configuration File Usage

Instead of hardcoding paths, use the configuration files:

```python
import yaml

# Load configuration
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access paths
data_root = config['data']['shanghaitech']['part_a']
checkpoint_path = config['models']['vmamba_tmtb']['checkpoint']
```

## Running Scripts After Migration

### Training

**Old:**

```bash
python finetune_vmamba.py --checkpoint checkpoints/jhu_5.pth --data-root datasets/...
```

**New:**

```bash
python src/models/train_vmamba.py --checkpoint saved_models/checkpoints/pretrained/jhu_5.pth --data-root data/raw/datasets/...
```

Or use the config file:

```bash
python src/models/train_vmamba.py --config config/config.yaml
```

### Data Preparation

**Old:**

```bash
python create_density_maps.py
```

**New:**

```bash
python src/data/create_density_maps.py
```

### Testing

**Old:**

```bash
python test_preprocessing.py
```

**New:**

```bash
python -m pytest tests/test_preprocessing.py
```

## Batch Update Commands

Use these commands to update import statements in multiple files:

### Windows (PowerShell):

```powershell
# Update model imports
Get-ChildItem -Recurse -Include *.py | ForEach-Object {
    (Get-Content $_.FullName) -replace 'from models\.', 'from src.models.architectures.' | Set-Content $_.FullName
}

# Update utils imports
Get-ChildItem -Recurse -Include *.py | ForEach-Object {
    (Get-Content $_.FullName) -replace 'from utils\.', 'from src.data.utils.' | Set-Content $_.FullName
}

# Update preprocessing imports
Get-ChildItem -Recurse -Include *.py | ForEach-Object {
    (Get-Content $_.FullName) -replace 'from preprocessing\.', 'from src.data.preprocessing.' | Set-Content $_.FullName
}
```

### Linux/Mac:

```bash
# Update model imports
find . -name "*.py" -exec sed -i 's/from models\./from src.models.architectures./g' {} +

# Update utils imports
find . -name "*.py" -exec sed -i 's/from utils\./from src.data.utils./g' {} +

# Update preprocessing imports
find . -name "*.py" -exec sed -i 's/from preprocessing\./from src.data.preprocessing./g' {} +
```

## Testing the Migration

After migration, verify everything works:

1. **Run tests:**

```bash
python -m pytest tests/
```

2. **Check imports:**

```bash
python -c "from src.models.architectures.vmamba_tmtb import VMambaTMTB"
python -c "from src.data.utils import preprocess"
```

3. **Verify config loading:**

```bash
python -c "import yaml; print(yaml.safe_load(open('config/config.yaml')))"
```

## Common Issues and Solutions

### Issue 1: ModuleNotFoundError

**Problem:** `ModuleNotFoundError: No module named 'models'`

**Solution:** Update import to use new path:

```python
from src.models.architectures.vmamba_tmtb import VMambaTMTB
```

### Issue 2: File Not Found

**Problem:** `FileNotFoundError: [Errno 2] No such file or directory: 'checkpoints/jhu_5.pth'`

**Solution:** Update path to:

```python
checkpoint_path = "saved_models/checkpoints/pretrained/jhu_5.pth"
```

### Issue 3: sys.path Issues

**Problem:** Python can't find src module

**Solution:** Add to top of script:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
```

Or install as package:

```bash
pip install -e .
```

## Next Steps

1. Update all Python files with new import statements
2. Update configuration files with correct paths
3. Test each module individually
4. Update documentation and README
5. Commit changes to version control

## Rollback Plan

If issues occur, old structure is preserved. To rollback:

1. Git revert to previous commit
2. Or manually restore from old directories (if not deleted yet)
