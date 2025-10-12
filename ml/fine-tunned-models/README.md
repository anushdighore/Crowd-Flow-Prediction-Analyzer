# Models Directory

This directory stores your **trained, fine-tuned, and corrected** models.

## 📝 What Goes Here?

✅ **Store here:**

- Corrected checkpoints (e.g., `tmtb_jhu_corrected.pth`)
- Fine-tuned models (e.g., `csrnet_finetuned_partA.pth`)
- Training checkpoints (e.g., `tmtb_epoch_50.pth`)
- Your experimental models

❌ **Do NOT store here:**

- Original pretrained checkpoints → Use `ml/checkpoints/` instead
- Downloaded model weights → Use `ml/checkpoints/` instead

## 🔒 Version Control

This directory is **ignored by Git** (.gitignore) because model files are too large.

### Sharing Models

For large models, use cloud storage:

```bash
# AWS S3
aws s3 cp tmtb_jhu_corrected.pth s3://your-bucket/models/

# Google Drive (using rclone)
rclone copy . gdrive:project/models/

# Download URL in README
wget https://your-cloud-storage/tmtb_jhu_corrected.pth
```

## 📂 File Naming Convention

Use descriptive names:

- `{model}_{dataset}_{version}.pth`
- Examples:
  - `tmtb_jhu_corrected.pth`
  - `csrnet_shanghaitech_partA_finetuned.pth`
  - `vmamba_jhu_epoch_100.pth`

## 💡 Usage

```python
from pathlib import Path
import torch

# Load model
models_dir = Path('ml/fine-tunned-models')
model_path = models_dir / 'tmtb_jhu_corrected.pth'
checkpoint = torch.load(model_path)

# Save model
save_path = models_dir / 'my_new_model.pth'
torch.save(model.state_dict(), save_path)
```

## 📊 Current Models

Run notebook cell to see list of models:

```python
from pathlib import Path
models = sorted(Path('ml/fine-tunned-models').glob('*.pth'))
for m in models:
    size = m.stat().st_size / (1024*1024)
    print(f'{m.name:<40} {size:>8.1f} MB')
```

---

See [docs/MODEL_STORAGE.md](../../docs/MODEL_STORAGE.md) for full documentation.
