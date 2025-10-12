# Fine-tuning VMamba TMTB for Crowd Counting

Complete solution for fine-tuning your existing VMamba TMTB checkpoint on ShanghaiTech dataset.

---

## 🎯 What This Is

You have a **VMamba TMTB checkpoint** (`checkpoints/jhu_5.pth`) trained on JHU dataset.

This guide shows you how to **fine-tune it on ShanghaiTech dataset** to adapt it for crowd counting.

**Why fine-tune?**

- ✅ Much faster than training from scratch (4-6 hours vs 2-3 days)
- ✅ You already have the checkpoint
- ✅ VMamba is more modern than CSRNet (2024 vs 2018)
- ✅ Transfer learning gives better results
- ✅ No need to download broken checkpoints

---

## 📁 Files Created

### Training & Testing

- **`finetune_vmamba.py`** - Complete fine-tuning script
- **`create_density_maps.py`** - Dataset preparation (converts .mat to .h5)
- **`test_finetuned.py`** - Test fine-tuned model on images
- **`evaluate_testset.py`** - Evaluate on full test set
- **`visualize_results.py`** - Create visualizations

### Documentation

- **`QUICKSTART_VMAMBA.md`** - Quick start guide (START HERE)
- **`DATASET_PREPARATION.md`** - Dataset download and setup
- **`TEST_FINETUNED_MODEL.md`** - Testing and deployment guide
- **`VMAMBA_FINETUNING_SUMMARY.md`** - Complete overview

---

## ⚡ Quick Start (5 Steps)

### 1. Download Dataset

```bash
# Using Kaggle
pip install kaggle
kaggle datasets download -d tthien/shanghaitech
unzip shanghaitech.zip -d datasets/
```

**Or download from Google Drive:**
https://drive.google.com/drive/folders/1CrdJkgDdwNw4g5D7D-q7wJxJpDlsWfM9

---

### 2. Generate Density Maps

```bash
python create_density_maps.py --root datasets/ShanghaiTech --part A
```

**Output:**

```
Processing part_A/train_data...
Found 300 images
Generating density maps: 100%|████████| 300/300 [01:23<00:00]
✅ Successfully processed 300/300 files
```

---

### 3. Fine-tune Model

```bash
python finetune_vmamba.py \
    --checkpoint checkpoints/jhu_5.pth \
    --data-root datasets/ShanghaiTech/part_A \
    --epochs 50 \
    --batch-size 8
```

**Expected training time:**

- GPU (GTX 1080 Ti): 4-6 hours
- GPU (RTX 3090): 2-3 hours

**Output:**

```
🏋️  Starting Training
Epoch 1/50: loss=0.0234, MAE=45.32
...
Epoch 50/50: loss=0.0089, MAE=58.34
🎉 Training Complete!
✅ Best MAE: 58.34
```

---

### 4. Test Model

```bash
# Single image
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image test_image.jpg

# Full test set evaluation
python evaluate_testset.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --data-root datasets/ShanghaiTech/part_A
```

**Output:**

```
📊 Test Set Results:
   MAE: 58.34
   RMSE: 82.45
```

---

### 5. Deploy API

```bash
# Start FastAPI server
uvicorn models.vmamba.api:app --reload --port 8000

# Test it
curl -X POST "http://localhost:8000/count" -F "file=@test_image.jpg"
```

---

## 📊 Expected Results

### ShanghaiTech Part A (Dense Crowds)

- **Good**: MAE 60-80
- **Excellent**: MAE < 60
- **State-of-the-art**: MAE 50-55

### ShanghaiTech Part B (Sparse Crowds)

- **Good**: MAE 8-12
- **Excellent**: MAE < 8
- **State-of-the-art**: MAE 6-7

---

## 📚 Documentation

### 1. Quick Start

👉 **Start here**: `QUICKSTART_VMAMBA.md`

- Complete step-by-step guide
- All commands in one place
- Troubleshooting tips

### 2. Dataset Preparation

👉 `DATASET_PREPARATION.md`

- Download instructions (3 methods)
- Directory structure
- Density map generation
- Verification scripts

### 3. Testing Guide

👉 `TEST_FINETUNED_MODEL.md`

- Single image testing
- Batch testing
- Model comparison
- API deployment

### 4. Complete Overview

👉 `VMAMBA_FINETUNING_SUMMARY.md`

- Why fine-tuning is better
- Complete workflow
- Expected results
- Comparison with alternatives

---

## 🔧 Scripts Reference

### Training Script

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

**Parameters:**

- `--checkpoint`: Pretrained VMamba checkpoint
- `--data-root`: Path to ShanghaiTech part_A or part_B
- `--output-dir`: Where to save fine-tuned models
- `--epochs`: Number of training epochs (default: 50)
- `--batch-size`: Batch size (reduce if OOM)
- `--lr`: Learning rate (default: 1e-5)
- `--device`: cuda or cpu

---

### Testing Script

```bash
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image test_image.jpg \
    --device cuda
```

**Features:**

- Single image testing
- Batch testing (pass directory path)
- Model comparison (use `--compare` flag)
- Visualization (density map + overlay)

---

### Evaluation Script

```bash
python evaluate_testset.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --data-root datasets/ShanghaiTech/part_A \
    --device cuda
```

**Outputs:**

- MAE (Mean Absolute Error)
- RMSE (Root Mean Square Error)
- Best/worst predictions
- Error statistics

---

### Visualization Script

```bash
python visualize_results.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_final.pth \
    --output-dir visualizations
```

**Creates:**

- Training loss curves
- MAE/MSE plots
- Error distribution
- Predictions grid

---

## 💡 Tips & Troubleshooting

### Problem: Out of Memory

**Solution:** Reduce batch size

```bash
python finetune_vmamba.py ... --batch-size 4
# or
python finetune_vmamba.py ... --batch-size 2
```

---

### Problem: Training Too Slow

**Solutions:**

1. Use Part B (smaller images):

   ```bash
   python finetune_vmamba.py --data-root datasets/ShanghaiTech/part_B ...
   ```

2. Reduce epochs:

   ```bash
   python finetune_vmamba.py ... --epochs 30
   ```

3. Use GPU (not CPU)

---

### Problem: High MAE (> 100)

**Possible causes:**

1. Not enough epochs → Train longer
2. Learning rate too high → Use `--lr 5e-6`
3. Dataset issues → Verify density maps
4. Batch size too small → Increase if you have memory

---

### Problem: Loss Not Decreasing

**Solution:** Unfreeze backbone layers

Edit `finetune_vmamba.py`, comment out lines ~150-152:

```python
# for param in model.backbone.parameters():
#     param.requires_grad = False
```

This trains the full model (slower but potentially better).

---

## 🎯 Complete Workflow Summary

```bash
# 1. Download dataset
kaggle datasets download -d tthien/shanghaitech
unzip shanghaitech.zip -d datasets/

# 2. Generate density maps
python create_density_maps.py --root datasets/ShanghaiTech --part A

# 3. Fine-tune
python finetune_vmamba.py \
    --checkpoint checkpoints/jhu_5.pth \
    --data-root datasets/ShanghaiTech/part_A \
    --epochs 50

# 4. Test
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image test_image.jpg

# 5. Evaluate
python evaluate_testset.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --data-root datasets/ShanghaiTech/part_A

# 6. Visualize
python visualize_results.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_final.pth

# 7. Deploy
uvicorn models.vmamba.api:app --reload --port 8000
```

---

## 📁 Directory Structure After Setup

```
d:\College\Major Project\
├── checkpoints/
│   ├── jhu_5.pth                                    # Original checkpoint
│   └── vmamba_finetuned/
│       ├── vmamba_shanghai_best.pth                 # Best model (USE THIS!)
│       ├── vmamba_shanghai_final.pth
│       ├── vmamba_shanghai_epoch10.pth
│       └── ...
│
├── datasets/
│   └── ShanghaiTech/
│       ├── part_A/
│       │   ├── train_data/
│       │   │   ├── images/ (300 .jpg)
│       │   │   └── ground-truth/ (300 .h5)
│       │   └── test_data/
│       │       ├── images/ (182 .jpg)
│       │       └── ground-truth/ (182 .h5)
│       └── part_B/
│           └── ...
│
├── models/
│   ├── vmamba_tmtb.py                              # Model architecture
│   └── vmamba/
│       └── api.py                                   # FastAPI server
│
├── finetune_vmamba.py                              # Training script
├── create_density_maps.py                          # Dataset preparation
├── test_finetuned.py                               # Testing script
├── evaluate_testset.py                             # Evaluation script
├── visualize_results.py                            # Visualization script
│
├── QUICKSTART_VMAMBA.md                            # Quick start guide
├── DATASET_PREPARATION.md                          # Dataset guide
├── TEST_FINETUNED_MODEL.md                         # Testing guide
├── VMAMBA_FINETUNING_SUMMARY.md                    # Complete overview
└── README_VMAMBA_FINETUNING.md                     # This file
```

---

## 🎉 You're Ready!

**Next steps:**

1. Read `QUICKSTART_VMAMBA.md` for detailed instructions
2. Download ShanghaiTech dataset
3. Run the 5-step quick start above
4. Test your fine-tuned model
5. Deploy to your React frontend

**Estimated time:**

- Dataset download: 10 minutes
- Density map generation: 3 minutes
- Fine-tuning: 4-6 hours (GPU)
- Testing: 10 minutes

**Total: ~5 hours** (mostly training)

Good luck! 🚀

---

## 📞 Need Help?

Check the documentation:

- **Quick start** → `QUICKSTART_VMAMBA.md`
- **Dataset setup** → `DATASET_PREPARATION.md`
- **Testing** → `TEST_FINETUNED_MODEL.md`
- **Complete overview** → `VMAMBA_FINETUNING_SUMMARY.md`
