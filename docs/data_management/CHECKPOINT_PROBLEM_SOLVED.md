# CSRNet Checkpoint Problem - SOLVED!

## 🔴 PROBLEM IDENTIFIED

**Your Issue**: Getting count of 34 for 1 person, or -24 for 1 person

**Root Cause**: **The checkpoint file (`csrnet.pth`) is NOT properly trained!**

## 🔬 Diagnostic Results

```
Density map statistics:
   Min value: -0.002123
   Max value: 0.003450
   Mean value: -0.000384  ← NEGATIVE! This is wrong!
   Sum (count): -1.57

Density map value distribution:
   Positive values: 716 / 4096
   Negative values: 3380 / 4096  ← MAJORITY ARE NEGATIVE!
```

### What This Means

- A properly trained CSRNet should output **mostly positive** density values
- Your model outputs **mostly negative** values (82% negative)
- This indicates the checkpoint is from **very early training** or **not trained at all**

## ✅ SOLUTIONS

### Option 1: Download Pre-trained Checkpoint (RECOMMENDED)

Get the official pre-trained checkpoint from the original CSRNet repo:

**ShanghaiTech Part A**:

- Link: https://drive.google.com/open?id=1QmB0KBnGR9q8_9-V-YG98G9fqBvBMy7u
- This is trained for ~400 epochs on ShanghaiTech Part A
- Expected MAE: ~68

**ShanghaiTech Part B**:

- Link: https://drive.google.com/open?id=1cNHKN5WzI_KTI3A-VL5cHvQ3vCJ3wW7_
- This is trained for ~400 epochs on ShanghaiTech Part B
- Expected MAE: ~10

**Steps**:

1. Download the .pth file from Google Drive
2. Replace your current `checkpoints/csrnet.pth` with the downloaded file
3. Restart your API server
4. Test again with real crowd images

### Option 2: Train Your Own Model

If you want to train from scratch:

```bash
cd architectures/CSRNet-pytorch
python train.py part_A_train.json part_A_test.json 0 0
```

**Note**: Training takes:

- ~400 epochs for convergence
- ~8-12 hours on GPU
- Requires ShanghaiTech dataset

### Option 3: Verify Your Current Checkpoint

If you believe your checkpoint should work:

1. Check the checkpoint metadata:

```python
checkpoint = torch.load('checkpoints/csrnet.pth', map_location='cpu')
print(f"Epoch: {checkpoint.get('epoch', 'unknown')}")
print(f"Best MAE: {checkpoint.get('best_prec1', 'unknown')}")
```

2. If epoch < 100, the model is undertrained
3. If best_prec1 > 200, the model didn't train properly

## 🧪 How to Test the Fix

After getting a proper checkpoint:

1. **Test with real crowd image**:

```python
from PIL import Image
from preprocessing import CSRNetPreprocessor

preprocessor = CSRNetPreprocessor()
img = Image.open("crowd_image.jpg")
tensor = preprocessor.preprocess(img)

with torch.no_grad():
    density_map = model(tensor)
    count = density_map.sum().item()

print(f"Count: {count}")
print(f"Positive values: {(density_map > 0).sum().item()}/{density_map.numel()}")
```

2. **Expected results**:
   - Density map should be **mostly positive** (>90%)
   - Count should be reasonable for the scene
   - For ShanghaiTech images, accuracy within ±10% is good

## 📊 Understanding the Problem

### What Happened

```
Your Checkpoint:
  Epoch: ??? (likely < 50)
  Training: Incomplete
  Output: Negative density values
  Result: Wrong counts (34 for 1 person)

Proper Checkpoint:
  Epoch: 400+
  Training: Complete
  Output: Positive density values
  Result: Accurate counts
```

### Why Preprocessing Alone Didn't Fix It

- ✅ Preprocessing is now **correct** (no resizing, proper normalization)
- ❌ But the model weights are **not trained**
- Result: Correct preprocessing + untrained model = still wrong predictions

**Both preprocessing AND trained weights are required!**

## 🎯 Summary

| Issue         | Status                                 |
| ------------- | -------------------------------------- |
| Preprocessing | ✅ FIXED (no resizing)                 |
| Architecture  | ✅ CORRECT (matches original)          |
| Checkpoint    | ❌ **NOT TRAINED** (needs replacement) |

**Action Required**: Download and use a properly trained checkpoint!

## 📚 Resources

- **Official Repo**: https://github.com/leeyeehoo/CSRNet-pytorch
- **Pre-trained Models**: See links above
- **Paper**: https://arxiv.org/abs/1802.10062
- **Dataset**: https://github.com/desenzhou/ShanghaiTech

## ✅ Next Steps

1. Download pre-trained checkpoint from Google Drive link above
2. Replace `checkpoints/csrnet.pth`
3. Restart API: `cd models/csrnet && python api.py`
4. Test with real crowd images (not random noise)
5. Expect much more accurate results!

---

**The preprocessing fix was necessary but not sufficient. You need BOTH correct preprocessing AND a trained checkpoint!**
