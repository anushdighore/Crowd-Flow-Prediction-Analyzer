# CSRNet Preprocessing - New Location Guide

## ✅ New Structure (Correct)

```
ml/
├── src/
│   ├── models/
│   │   └── csrnet/
│   │       └── csrnet.py           # CSRNet model
│   ├── preprocessing/               # ← NEW LOCATION
│   │   ├── __init__.py
│   │   └── csrnet_preprocess.py    # ← Preprocessing module HERE
│   └── utils/
│       └── 5-csrnet-check.ipynb
├── datasets/
│   ├── images/                      # Sample crowd images
│   └── preprocessing/               # ⚠️ OLD - Can be deleted
└── checkpoints/
    └── csrnet.pth
```

## 📦 How to Import

### In Notebooks (from `ml/src/utils/`)

```python
from preprocessing import CSRNetPreprocessor
```

### In Python Scripts (from `ml/src/`)

```python
from preprocessing import CSRNetPreprocessor
```

### In Backend/API

```python
# Update the backend to point to the new location
import sys
sys.path.insert(0, '/path/to/ml/src')
from preprocessing import CSRNetPreprocessor
```

## 🔄 Migration Steps

1. ✅ Created `ml/src/preprocessing/` directory
2. ✅ Copied `csrnet_preprocess.py` to new location
3. ✅ Created `__init__.py` for proper imports
4. ✅ Updated notebook import paths
5. 🔲 Delete old `ml/datasets/preprocessing/` (optional cleanup)
6. 🔲 Update backend API imports if needed

## 🎯 Why This is Better

- **Logical organization**: Code stays with code, data stays with data
- **Cleaner imports**: `from preprocessing import X` is intuitive
- **Standard ML structure**: Follows industry best practices
- **Easier maintenance**: All source code in one place (`ml/src/`)

## 📝 Files to Update

If you have other files importing the preprocessor, update them:

- ✅ `ml/src/utils/5-csrnet-check.ipynb` - Already updated
- 🔲 `backend/app/api/v1/endpoints/csrnet.py` - Update import path
- 🔲 Any training scripts
- 🔲 Any other notebooks

The import remains the same: `from preprocessing import CSRNetPreprocessor`
Just make sure the path is added to `sys.path`.
