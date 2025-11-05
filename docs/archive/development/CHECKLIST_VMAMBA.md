# VMamba Fine-tuning Checklist

Track your progress through the fine-tuning process.

---

## 📋 Pre-flight Checklist

### Prerequisites

- [ ] Python 3.8+ installed
- [ ] CUDA-capable GPU available (or willing to use CPU)
- [ ] At least 10GB free disk space for dataset
- [ ] Internet connection for downloads

### Python Packages

```bash
pip install torch torchvision
pip install h5py scipy pillow
pip install tqdm matplotlib
pip install fastapi uvicorn
pip install kaggle  # For dataset download
```

- [ ] PyTorch installed (`torch`, `torchvision`)
- [ ] Data processing libraries (`h5py`, `scipy`, `pillow`)
- [ ] Training utilities (`tqdm`, `matplotlib`)
- [ ] API framework (`fastapi`, `uvicorn`)
- [ ] Kaggle CLI (`kaggle`) - optional

### Verify Existing Files

- [ ] `checkpoints/jhu_5.pth` exists
- [ ] `models/vmamba_tmtb.py` exists
- [ ] All training scripts downloaded

---

## 🎯 Phase 1: Dataset Setup

### Download Dataset

**Method 1: Kaggle** (Recommended)

- [ ] Install Kaggle CLI: `pip install kaggle`
- [ ] Setup Kaggle API key (see instructions below)
- [ ] Download: `kaggle datasets download -d tthien/shanghaitech`
- [ ] Extract: `unzip shanghaitech.zip -d datasets/`

**Method 2: Google Drive**

- [ ] Visit: https://drive.google.com/drive/folders/1CrdJkgDdwNw4g5D7D-q7wJxJpDlsWfM9
- [ ] Download `ShanghaiTech.zip`
- [ ] Extract to `datasets/ShanghaiTech/`

**Method 3: Direct Download**

- [ ] Clone: `git clone https://github.com/desenzhou/ShanghaiTechDataset.git`
- [ ] Move to `datasets/ShanghaiTech/`

### Verify Dataset Structure

- [ ] `datasets/ShanghaiTech/part_A/train_data/images/` exists (300 images)
- [ ] `datasets/ShanghaiTech/part_A/train_data/ground_truth/` exists (300 .mat files)
- [ ] `datasets/ShanghaiTech/part_A/test_data/images/` exists (182 images)
- [ ] `datasets/ShanghaiTech/part_A/test_data/ground_truth/` exists (182 .mat files)

### Generate Density Maps

- [ ] Run: `python create_density_maps.py --root datasets/ShanghaiTech --part A`
- [ ] Verify: `datasets/ShanghaiTech/part_A/train_data/ground-truth/` created (300 .h5 files)
- [ ] Verify: `datasets/ShanghaiTech/part_A/test_data/ground-truth/` created (182 .h5 files)
- [ ] Run verification: `python create_density_maps.py --verify-only --part A`

**Expected output:**

```
✅ Successfully processed 300/300 files (train)
✅ Successfully processed 182/182 files (test)
✅ All files matched!
```

---

## 🏋️ Phase 2: Fine-tuning

### Prepare Training

- [ ] Check GPU available: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Verify checkpoint: `dir checkpoints\jhu_5.pth`
- [ ] Create output directory: `mkdir checkpoints\vmamba_finetuned`

### Start Training

- [ ] Run training script:

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

### Monitor Training

- [ ] Training started successfully
- [ ] Loss decreasing over epochs
- [ ] MAE decreasing over epochs
- [ ] Checkpoints being saved every 10 epochs
- [ ] Best model saved when MAE improves

**Training Progress:**

- [ ] Epoch 10/50 completed
- [ ] Epoch 20/50 completed
- [ ] Epoch 30/50 completed
- [ ] Epoch 40/50 completed
- [ ] Epoch 50/50 completed

### Training Complete

- [ ] Training finished successfully
- [ ] `vmamba_shanghai_best.pth` created
- [ ] `vmamba_shanghai_final.pth` created
- [ ] Best MAE recorded: **\_\_\_\_**

**Target MAE:**

- Part A: < 60 is excellent
- Part B: < 8 is excellent

---

## 🧪 Phase 3: Testing

### Single Image Test

- [ ] Prepare test image (any crowd photo)
- [ ] Run: `python test_finetuned.py --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth --image test_image.jpg`
- [ ] Visualization displayed correctly
- [ ] Count looks reasonable

### Batch Test

- [ ] Run on test directory:

```bash
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image datasets/ShanghaiTech/part_A/test_data/images/
```

- [ ] Counts printed for all images
- [ ] Most counts look reasonable

### Compare Before/After

- [ ] Run comparison:

```bash
python test_finetuned.py \
    --checkpoint checkpoints/jhu_5.pth \
    --compare checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image test_image.jpg
```

- [ ] Fine-tuned model performs better
- [ ] Visualization shows improvement

---

## 📊 Phase 4: Evaluation

### Full Test Set Evaluation

- [ ] Run: `python evaluate_testset.py --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth --data-root datasets/ShanghaiTech/part_A`
- [ ] MAE calculated: **\_\_\_\_**
- [ ] RMSE calculated: **\_\_\_\_**
- [ ] Results meet expectations (MAE < 60 for Part A)

### Visualize Results

- [ ] Run: `python visualize_results.py --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_final.pth --output-dir visualizations`
- [ ] Training history plot created
- [ ] Loss curves look good (decreasing)
- [ ] MAE curve shows improvement

---

## 🚀 Phase 5: Deployment

### Create API

- [ ] Create `models/vmamba/` directory
- [ ] Create `models/vmamba/api.py` (see TEST_FINETUNED_MODEL.md)
- [ ] Update checkpoint path in API code

### Test API Locally

- [ ] Start server: `uvicorn models.vmamba.api:app --reload --port 8000`
- [ ] Server starts without errors
- [ ] Visit: http://localhost:8000
- [ ] API documentation visible

### Test API Endpoint

- [ ] Test with curl:

```bash
curl -X POST "http://localhost:8000/count" -F "file=@test_image.jpg"
```

- [ ] Response received
- [ ] Count looks correct
- [ ] Response format correct (JSON with count field)

### Test with Python

```python
import requests
files = {'file': open('test_image.jpg', 'rb')}
response = requests.post('http://localhost:8000/count', files=files)
print(response.json())
```

- [ ] Python test works
- [ ] Count matches CLI test

---

## 🎨 Phase 6: Frontend Integration

### Update React Frontend

- [ ] Update API endpoint URL in `src/App.js`
- [ ] Test file upload from frontend
- [ ] Count displayed correctly in UI
- [ ] Error handling works

### End-to-End Test

- [ ] Upload image from React app
- [ ] Image sent to FastAPI backend
- [ ] Prediction returned
- [ ] Count displayed in frontend
- [ ] Density map visualization (optional)

---

## ✅ Final Verification

### Model Quality

- [ ] MAE < 60 (Part A) or MAE < 8 (Part B)
- [ ] Visual inspection: predictions look reasonable
- [ ] No negative counts
- [ ] No wildly incorrect counts (e.g., 1000 for empty room)

### System Integration

- [ ] Backend API running
- [ ] Frontend connected
- [ ] End-to-end flow working
- [ ] Error handling tested

### Documentation

- [ ] Understand what fine-tuning did
- [ ] Know how to retrain if needed
- [ ] Can explain results to others
- [ ] Saved all checkpoints and logs

---

## 🎉 Success Criteria

You've successfully fine-tuned VMamba if:

- ✅ Training completed without errors
- ✅ Best MAE < 60 (Part A) or < 8 (Part B)
- ✅ Model predicts reasonable counts on test images
- ✅ API serves predictions correctly
- ✅ Frontend displays results

---

## 🆘 Troubleshooting

### If training fails:

- [ ] Checked error message
- [ ] Reduced batch size (--batch-size 4 or 2)
- [ ] Verified dataset structure
- [ ] Checked GPU memory available

### If predictions are bad:

- [ ] Verified dataset was prepared correctly
- [ ] Checked if training converged (loss decreased)
- [ ] Tried training for more epochs
- [ ] Compared with original checkpoint (pre-finetuning)

### If API fails:

- [ ] Checked checkpoint path is correct
- [ ] Verified all imports work
- [ ] Tested with simple test image first
- [ ] Checked port 8000 is not already in use

---

## 📝 Notes Section

**Dataset downloaded from:** ********\_\_\_\_********

**Training started:** ********\_\_\_\_********

**Training completed:** ********\_\_\_\_********

**Training time:** \_\_\_\_ hours

**Best MAE achieved:** ********\_\_\_\_********

**Final model location:** ********\_\_\_\_********

**Any issues encountered:**

-
-
-

**Solutions that worked:**

-
-
-

---

## 🎓 What You Learned

- [ ] Transfer learning / fine-tuning
- [ ] Crowd counting with density maps
- [ ] PyTorch training loops
- [ ] Model evaluation (MAE, RMSE)
- [ ] FastAPI deployment
- [ ] State-space models (VMamba)

---

## 📚 Reference

**Key Files:**

- `README_VMAMBA_FINETUNING.md` - Main README
- `QUICKSTART_VMAMBA.md` - Quick start guide
- `DATASET_PREPARATION.md` - Dataset setup
- `TEST_FINETUNED_MODEL.md` - Testing guide
- `VMAMBA_FINETUNING_SUMMARY.md` - Complete overview
- `WHY_FINETUNE_VMAMBA.md` - Comparison analysis

**Scripts:**

- `finetune_vmamba.py` - Training script
- `create_density_maps.py` - Dataset preparation
- `test_finetuned.py` - Testing script
- `evaluate_testset.py` - Evaluation script
- `visualize_results.py` - Visualization script

---

## ✨ Congratulations!

Once all checkboxes are complete, you have successfully:

- Fine-tuned VMamba TMTB on ShanghaiTech
- Deployed a working crowd counting API
- Integrated with your React frontend
- Achieved state-of-the-art accuracy

🎉 Great work! 🎉
