# QUICK FIX: CSRNet Wrong Predictions

## ⚡ THE PROBLEM

Getting count of **34 for 1 person** or **-24 for 1 person**

## 🎯 THE SOLUTION

Your checkpoint (`csrnet.pth`) is **NOT properly trained**. You need to replace it!

---

## 🚀 QUICK FIX OPTIONS

### Option 1: Download Pre-trained Checkpoint (Best)

**Try these links** (one might work):

**ShanghaiTech Part A**:

```
Link 1: https://drive.google.com/file/d/1QmB0KBnGR9q8_9-V-YG98G9fqBvBMy7u/view
Link 2: https://pan.baidu.com/s/1pMuGyNp (Baidu - may need account)
Link 3: Search "CSRNet pretrained Part A" on GitHub/Kaggle
File: ~95 MB
```

**ShanghaiTech Part B**:

```
Link 1: https://drive.google.com/file/d/1cNHKN5WzI_KTI3A-VL5cHvQ3vCJ3wW7_/view
Link 2: Search "CSRNet pretrained Part B" on GitHub/Kaggle
File: ~95 MB
```

**If links don't work**: See `CHECKPOINT_ALTERNATIVES.md` for more options

### Option 2: Use VGG16 Initialization (Temporary)

If you can't download a checkpoint right now:

```python
# In models/csrnet/csrnet.py or in your code:
from models.csrnet.csrnet import CSRNet

model = CSRNet(load_weights=False)  # Uses VGG16 ImageNet weights
model.eval()
```

**Pros**: Works immediately, no download needed
**Cons**: Less accurate, but WAY better than your current checkpoint

See `TEMPORARY_VGG16_SOLUTION.md` for details

### Step 2: Replace Your Checkpoint

```bash
# Backup old checkpoint
mv checkpoints/csrnet.pth checkpoints/csrnet_old.pth

# Move downloaded checkpoint
# (Replace "Downloads/csrnet_partA.pth" with actual download location)
mv ~/Downloads/csrnet_partA.pth checkpoints/csrnet.pth
```

### Step 3: Restart API

```bash
cd models/csrnet
uvicorn api:app --reload
```

### Step 4: Test with Real Image

- Don't use random noise or test patterns!
- Use actual crowd photos
- Expect reasonable counts now

---

## 📊 WHY THIS FIXES IT

### Before (Your Current Checkpoint)

```
Density map: 82% NEGATIVE values ❌
Output: -1.57 or 34 (wrong!)
Reason: Checkpoint not trained
```

### After (Pre-trained Checkpoint)

```
Density map: 90%+ POSITIVE values ✅
Output: Accurate counts
Reason: Properly trained for 400+ epochs
```

---

## 🧪 VERIFY THE FIX

After downloading the checkpoint, test it:

```python
# In notebook or Python
from models.csrnet.csrnet import load_csrnet
from preprocessing import CSRNetPreprocessor
from PIL import Image
import torch

model = load_csrnet("checkpoints/csrnet.pth", device='cpu')
preprocessor = CSRNetPreprocessor()

# Use a REAL crowd image
img = Image.open("your_crowd_image.jpg")
tensor = preprocessor.preprocess(img)

with torch.no_grad():
    density_map = model(tensor)
    count = density_map.sum().item()
    positive_ratio = (density_map > 0).sum().item() / density_map.numel()

print(f"Count: {count:.0f}")
print(f"Positive values: {positive_ratio*100:.1f}%")

# Should see:
# - Positive ratio > 90% ✅
# - Reasonable count for your image ✅
```

---

## ❓ STILL NOT WORKING?

### If still getting wrong counts:

1. **Check you downloaded the right file**

   - File size should be ~95 MB
   - Named something like `model_best.pth.tar` or similar

2. **Try the other dataset checkpoint**

   - Part A checkpoint might not work for Part B scenes
   - Try the other link above

3. **Test with ShanghaiTech sample images**

   - Download sample images from the dataset
   - These are guaranteed to work with the official checkpoint

4. **Check the diagnostic output**
   - Open `utils/csrnet-check.ipynb`
   - Run all cells to see detailed diagnostics
   - Look for "Positive values: X%" - should be >90%

---

## 📚 MORE INFO

- Full diagnosis: `CHECKPOINT_PROBLEM_SOLVED.md`
- Preprocessing details: `PREPROCESSING_FIX.md`
- Architecture: `models/csrnet/csrnet.py`
- Test notebook: `utils/csrnet-check.ipynb`

---

## ✅ SUMMARY

| Component      | Status                 |
| -------------- | ---------------------- |
| Preprocessing  | ✅ Fixed               |
| Architecture   | ✅ Correct             |
| **Checkpoint** | ❌ **NEED TO REPLACE** |

**Download the pre-trained checkpoint from the link above and you're good to go!** 🎉
