# 🚀 VMamba Fine-tuning Quick Start Guide

Complete guide to fine-tune your existing VMamba TMTB checkpoint on ShanghaiTech dataset.

---

## ⚡ TL;DR - Quick Commands

```bash
# 1. Download dataset (choose one method)
kaggle datasets download -d tthien/shanghaitech
unzip shanghaitech.zip -d datasets/

# 2. Generate density maps
python create_density_maps.py --root datasets/ShanghaiTech --part A

# 3. Fine-tune
python finetune_vmamba.py \
    --checkpoint checkpoints/jhu_5.pth \
    --data-root datasets/ShanghaiTech/part_A \
    --epochs 50 \
    --batch-size 8

# 4. Test
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image test_image.jpg

# 5. Deploy
uvicorn models.vmamba.api:app --reload --port 8000
```

---

## 📋 Prerequisites

### 1. Install Dependencies

```bash
pip install torch torchvision
pip install h5py scipy pillow
pip install tqdm matplotlib
pip install fastapi uvicorn
pip install kaggle  # For dataset download
```

### 2. Check Your Checkpoint

Verify you have the VMamba checkpoint:

```bash
dir checkpoints\jhu_5.pth
```

Should show: `checkpoints/jhu_5.pth` exists

---

## 📥 Step 1: Download Dataset

### Option A: Kaggle (Recommended)

```bash
# Install Kaggle
pip install kaggle

# Configure API key (first time only)
# 1. Go to https://www.kaggle.com/account
# 2. Create API token -> downloads kaggle.json
# 3. Move to: C:\Users\<YourName>\.kaggle\kaggle.json

# Download dataset
kaggle datasets download -d tthien/shanghaitech
unzip shanghaitech.zip -d datasets/
```

### Option B: Google Drive

1. Go to: https://drive.google.com/drive/folders/1CrdJkgDdwNw4g5D7D-q7wJxJpDlsWfM9
2. Download `ShanghaiTech.zip`
3. Extract to `datasets/ShanghaiTech/`

### Option C: Direct Download

```bash
# Create directory
mkdir datasets
cd datasets

# Download from mirror
curl -L -o shanghaitech.zip https://github.com/desenzhou/ShanghaiTechDataset/archive/refs/heads/master.zip
unzip shanghaitech.zip
```

---

## 🔧 Step 2: Prepare Dataset

### Check structure:

```
datasets/ShanghaiTech/
├── part_A/
│   ├── train_data/
│   │   ├── images/          # 300 images
│   │   └── ground_truth/    # .mat annotation files
│   └── test_data/
│       ├── images/          # 182 images
│       └── ground_truth/    # .mat annotation files
└── part_B/
    └── ...
```

### Generate density maps:

```bash
# For Part A (dense crowds)
python create_density_maps.py --root datasets/ShanghaiTech --part A

# For Part B (sparse crowds)
python create_density_maps.py --root datasets/ShanghaiTech --part B
```

This converts `.mat` files to `.h5` density maps.

**Expected output:**

```
Processing A_train_data...
100%|████████████████████| 300/300 [01:23<00:00]
✅ Processed 300 files

Processing A_test_data...
100%|████████████████████| 182/182 [00:51<00:00]
✅ Processed 182 files
```

---

## 🏋️ Step 3: Fine-tune Model

### Start training:

```bash
python finetune_vmamba.py \
    --checkpoint checkpoints/jhu_5.pth \
    --data-root datasets/ShanghaiTech/part_A \
    --output-dir checkpoints/vmamba_finetuned \
    --epochs 50 \
    --batch-size 8 \
    --lr 1e-5 \
    --device cuda
```

### What happens:

1. **Loads** your existing `jhu_5.pth` checkpoint
2. **Trains** regression head on ShanghaiTech (keeps backbone frozen)
3. **Saves** checkpoints every 10 epochs
4. **Tracks** best model based on MAE (Mean Absolute Error)

### Expected output:

```
📦 Loading pretrained checkpoint: checkpoints/jhu_5.pth
✅ Model loaded successfully
🎯 Training regression head only (faster)
   Trainable parameters: 1,234,567

📂 Loading data from: datasets/ShanghaiTech/part_A
   Train samples: 300
   Test samples: 182

🏋️  Starting Training
======================================================================

Epoch 1/50
----------------------------------------------------------------------
Epoch 1: 100%|██████████| 38/38 [02:15<00:00, loss=0.0234, MAE=45.32]
Validating: 100%|████████| 182/182 [01:05<00:00]

📊 Epoch 1 Results:
   Train - Loss: 0.0234, MAE: 45.32, MSE: 65.21
   Val   - Loss: 0.0198, MAE: 68.45, MSE: 98.76
   LR: 1.00e-05
   ✅ Saved best model (MAE: 68.45)

...

Epoch 50/50
----------------------------------------------------------------------
📊 Epoch 50 Results:
   Train - Loss: 0.0089, MAE: 18.23, MSE: 25.67
   Val   - Loss: 0.0102, MAE: 58.34, MSE: 82.45
   💾 Saved checkpoint: epoch50.pth

🎉 Training Complete!
======================================================================
✅ Best MAE: 58.34
📁 Models saved to: checkpoints/vmamba_finetuned
   - vmamba_shanghai_best.pth (MAE: 58.34)
   - vmamba_shanghai_final.pth (final epoch)
```

### Training time:

- **GPU (GTX 1080 Ti)**: 4-6 hours
- **GPU (RTX 3090)**: 2-3 hours
- **CPU**: Not recommended (20+ hours)

### If out of memory:

```bash
# Reduce batch size
python finetune_vmamba.py ... --batch-size 4

# Or even smaller
python finetune_vmamba.py ... --batch-size 2
```

---

## 🧪 Step 4: Test Model

### Single image test:

```bash
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image test_image.jpg
```

**Output:**

- Shows original image
- Shows density map
- Shows overlay
- Prints count

### Batch test:

```bash
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image datasets/ShanghaiTech/part_A/test_data/images/
```

### Compare before/after fine-tuning:

```bash
python test_finetuned.py \
    --checkpoint checkpoints/jhu_5.pth \
    --compare checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image test_image.jpg
```

---

## 📊 Step 5: Evaluate on Test Set

```bash
python evaluate_testset.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --data-root datasets/ShanghaiTech/part_A
```

**Expected output:**

```
📊 Test Set Results:
   MAE: 58.34
   RMSE: 82.45
   Min Error: 1.23
   Max Error: 245.67
   Median Error: 45.23

⚠️  Worst 5 Predictions:
   GT: 1234, Pred: 989.5, Error: 244.5
   ...

✅ Best 5 Predictions:
   GT: 145, Pred: 146.2, Error: 1.2
   ...
```

### Target metrics:

- **Part A**: MAE < 60 is excellent
- **Part B**: MAE < 8 is excellent

---

## 🚀 Step 6: Deploy with FastAPI

### Create API file:

Save this as `models/vmamba/api.py`:

```python
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import torch
from torchvision import transforms
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.vmamba_tmtb import VMambaTMTB

app = FastAPI(title="VMamba Crowd Counter")

# Load fine-tuned model
CHECKPOINT_PATH = "checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth"
device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = VMambaTMTB()
checkpoint = torch.load(CHECKPOINT_PATH, map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])
model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225])
])

@app.post("/count")
async def count_people(file: UploadFile = File(...)):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert('RGB')
    img_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        density_map = model(img_tensor)

    count = density_map.sum().item()

    return {
        "count": round(count, 1),
        "model": "VMamba-TMTB (fine-tuned)",
        "mae": checkpoint.get('best_mae', 'N/A')
    }

@app.get("/")
def root():
    return {
        "message": "VMamba Crowd Counter API",
        "model": "VMamba-TMTB",
        "trained_on": "ShanghaiTech Part A"
    }
```

### Run server:

```bash
uvicorn models.vmamba.api:app --reload --port 8000
```

### Test API:

```bash
# Using curl
curl -X POST "http://localhost:8000/count" \
     -F "file=@test_image.jpg"

# Using Python
import requests
files = {'file': open('test_image.jpg', 'rb')}
response = requests.post('http://localhost:8000/count', files=files)
print(response.json())
```

---

## 🎨 Step 7: Update React Frontend

Update your frontend to use the new API:

```javascript
// src/App.js
const handleUpload = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:8000/count", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  console.log(`Count: ${data.count}`);
  console.log(`Model: ${data.model}`);
  console.log(`MAE: ${data.mae}`);

  setCount(data.count);
};
```

---

## 💡 Tips & Troubleshooting

### Problem: Out of memory

**Solution:** Reduce batch size

```bash
python finetune_vmamba.py ... --batch-size 4
# or
python finetune_vmamba.py ... --batch-size 2
```

### Problem: Training too slow

**Solution 1:** Use Part B (smaller images)

```bash
python finetune_vmamba.py \
    --data-root datasets/ShanghaiTech/part_B \
    ...
```

**Solution 2:** Train on GPU (not CPU)

**Solution 3:** Reduce epochs

```bash
python finetune_vmamba.py ... --epochs 30
```

### Problem: High MAE (> 100)

**Possible causes:**

1. Not enough epochs (train longer)
2. Learning rate too high (reduce to `--lr 5e-6`)
3. Dataset not prepared correctly (check density maps)
4. Batch size too small (increase to 16 if you have memory)

### Problem: Loss not decreasing

**Solution:** Unfreeze backbone layers

Edit `finetune_vmamba.py`, comment out:

```python
# for param in model.backbone.parameters():
#     param.requires_grad = False
```

This trains the full model (slower but potentially better).

---

## 🎯 Expected Timeline

| Task                  | Time (GPU) | Time (CPU) |
| --------------------- | ---------- | ---------- |
| Download dataset      | 5-10 min   | 5-10 min   |
| Generate density maps | 2-3 min    | 5-10 min   |
| Fine-tune (50 epochs) | 4-6 hours  | 20+ hours  |
| Test & evaluate       | 5-10 min   | 30-60 min  |
| Deploy API            | 1 min      | 1 min      |

**Total**: ~5 hours (GPU) or ~22 hours (CPU)

---

## 📚 Files Created

After following this guide, you'll have:

```
checkpoints/
├── jhu_5.pth                                    # Original checkpoint
└── vmamba_finetuned/
    ├── vmamba_shanghai_best.pth                 # Best model (use this!)
    ├── vmamba_shanghai_final.pth                # Final epoch
    ├── vmamba_shanghai_epoch10.pth              # Intermediate
    ├── vmamba_shanghai_epoch20.pth              # Intermediate
    └── ...

datasets/
└── ShanghaiTech/
    └── part_A/
        ├── train_data/
        │   ├── images/ (300 .jpg)
        │   └── ground-truth/ (300 .h5)          # Generated
        └── test_data/
            ├── images/ (182 .jpg)
            └── ground-truth/ (182 .h5)          # Generated

models/
└── vmamba/
    └── api.py                                   # API server

Scripts:
├── finetune_vmamba.py                          # Training script
├── test_finetuned.py                           # Testing script
├── evaluate_testset.py                         # Evaluation script
├── create_density_maps.py                      # Data preparation
└── visualize_results.py                        # Visualization
```

---

## 🎉 You're Done!

Your VMamba model is now:

- ✅ Fine-tuned on ShanghaiTech
- ✅ Tested and evaluated
- ✅ Deployed with FastAPI
- ✅ Ready for your React frontend

**Next steps:**

1. Test with your own images
2. Compare results with CSRNet
3. Deploy to production
4. Celebrate! 🎊

---

## 📞 Need Help?

Check these guides:

- `DATASET_PREPARATION.md` - Detailed dataset setup
- `TEST_FINETUNED_MODEL.md` - Testing examples
- `ALTERNATIVE_MODELS.md` - Other model options

Good luck! 🚀
