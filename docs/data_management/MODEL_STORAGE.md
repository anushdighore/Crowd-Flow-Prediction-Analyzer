# Model Storage Organization

## 📂 Directory Structure

```
ml/
├── checkpoints/          ← Original pretrained weights (read-only)
│   ├── .gitkeep         (tracked by Git)
│   ├── jhu_5.pth        (TMTB original - 336 MB)
│   ├── csrnet.pth       (CSRNet original)
│   └── ...
│
└── models/              ← Corrected/trained/fine-tuned models (read-write)
    ├── .gitkeep         (tracked by Git)
    ├── tmtb_jhu_corrected.pth  (Key-fixed version)
    ├── csrnet_finetuned.pth    (Your trained models)
    └── ...
```

## 🎯 Purpose

### `ml/checkpoints/` - Original Checkpoints

- Store **original pretrained** weights downloaded from external sources
- **Read-only** - do NOT modify these files
- Version controlled (committed to Git or use Git LFS)
- Examples:
  - `jhu_5.pth` - Original TMTB checkpoint from JHU-Crowd++ paper
  - `csrnet.pth` - Original CSRNet checkpoint from ShanghaiTech

### `ml/fine-tunned-models/` - Trained/Corrected Models

- Store **your trained, fine-tuned, or corrected** models
- **Read-write** - safe to modify and experiment
- NOT version controlled (ignored by .gitignore - too large)
- Use cloud storage (AWS S3, Google Drive) for sharing
- Examples:
  - `tmtb_jhu_corrected.pth` - Fixed key mismatches
  - `csrnet_finetuned_partA.pth` - Fine-tuned on ShanghaiTech Part A
  - `tmtb_epoch_50.pth` - Training checkpoint at epoch 50

## 🔒 Version Control

### .gitignore Configuration

```gitignore
# Ignore all models in ml/fine-tunned-models/ (too large)
ml/fine-tunned-models/*.pth
ml/fine-tunned-models/*.pt

# Keep directory structure
!ml/fine-tunned-models/.gitkeep
!ml/checkpoints/.gitkeep

# Optional: Ignore checkpoints too (use Git LFS or download script)
ml/checkpoints/*.pth
```

### Best Practices

1. **Small models** (<100 MB): Can commit directly to Git
2. **Large models** (>100 MB):

   - Use Git LFS (Git Large File Storage)
   - Or store in cloud and provide download links
   - Or add to .gitignore and document separately

3. **Sharing Models:**

   ```bash
   # Upload to cloud
   aws s3 cp ml/fine-tunned-models/tmtb_jhu_corrected.pth s3://your-bucket/

   # Or Google Drive
   rclone copy ml/fine-tunned-models/ gdrive:models/

   # Share download link in README
   ```

## 📝 Usage Examples

### Loading Original Checkpoint

```python
from pathlib import Path
from models.tmtb.vmamba_official import load_tmtb_model

checkpoint_path = Path('ml/checkpoints/jhu_5.pth')
model = load_tmtb_model(str(checkpoint_path), device='cuda')
```

### Saving Corrected/Trained Model

```python
import torch
from pathlib import Path

models_dir = Path('ml/fine-tunned-models')
models_dir.mkdir(exist_ok=True)

# Save your trained model
save_path = models_dir / 'tmtb_jhu_corrected.pth'
torch.save(model.state_dict(), save_path)
print(f'✅ Saved to: {save_path}')
```

### Loading Your Trained Model

```python
from pathlib import Path
from models.tmtb.vmamba_official import load_tmtb_model

# Load your corrected/trained model
model_path = Path('ml/fine-tunned-models/tmtb_jhu_corrected.pth')
model = load_tmtb_model(str(model_path), device='cuda')
```

## 🚀 Migration Guide

If you have existing models in wrong locations:

```bash
# Move to correct location
mv ml/checkpoints/my_trained_model.pth ml/fine-tunned-models/
mv ml/checkpoints/jhu_5_corrected.pth ml/fine-tunned-models/tmtb_jhu_corrected.pth

# Keep only original checkpoints in ml/checkpoints/
# Everything else goes to ml/fine-tunned-models/
```

## 📊 File Size Guidelines

| File Type                  | Typical Size        | Storage                |
| -------------------------- | ------------------- | ---------------------- |
| Original TMTB checkpoint   | ~336 MB             | ml/checkpoints/        |
| Original CSRNet checkpoint | ~60 MB              | ml/checkpoints/        |
| Corrected checkpoints      | Same as original    | ml/fine-tunned-models/ |
| Training checkpoints       | Varies              | ml/fine-tunned-models/ |
| Fine-tuned models          | Similar to original | ml/fine-tunned-models/ |

## ✅ Verification

Run this cell in notebook to verify structure:

```python
from pathlib import Path

ml_dir = Path('ml')
checkpoints_dir = ml_dir / 'checkpoints'
models_dir = ml_dir / 'models'

print('📁 Directory Structure:')
print(f'   Checkpoints: {checkpoints_dir.exists()} ✅' if checkpoints_dir.exists() else f'   Checkpoints: ❌')
print(f'   Models: {models_dir.exists()} ✅' if models_dir.exists() else f'   Models: ❌')

if checkpoints_dir.exists():
    checkpoints = list(checkpoints_dir.glob('*.pth'))
    print(f'\n📦 Original Checkpoints: {len(checkpoints)}')
    for ckpt in checkpoints:
        size_mb = ckpt.stat().st_size / (1024*1024)
        print(f'   - {ckpt.name} ({size_mb:.1f} MB)')

if models_dir.exists():
    trained = list(models_dir.glob('*.pth'))
    print(f'\n🎯 Trained Models: {len(trained)}')
    for model in trained:
        size_mb = model.stat().st_size / (1024*1024)
        print(f'   - {model.name} ({size_mb:.1f} MB)')
```

## 📚 References

- **2-architecture_model_checks.ipynb** - Updated to use this structure
- **6-tmtb-check.ipynb** - Uses ml/checkpoints/ for loading
- **.gitignore** - Configured to ignore ml/fine-tunned-models/\*.pth

---

**Last Updated:** October 9, 2025  
**Status:** ✅ Production Ready
