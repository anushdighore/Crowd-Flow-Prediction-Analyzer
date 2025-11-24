# CSRNet Model Testing Notebook - Overview

## 📓 Notebook: `5-csrnet-check.ipynb`

**Location:** `ml/src/utils/5-csrnet-check.ipynb`

---

## 📋 What This Notebook Does

This notebook is a **complete testing and diagnostic tool** for your CSRNet crowd counting model. It validates the model architecture, loads weights, runs inference, and helps debug any issues.

---

## 🔢 Cell-by-Cell Breakdown

### Cell 1: Title (Markdown)

- Overview of the notebook purpose

### Cell 2: Setup & Imports ✅

**What it does:**

- Sets up Python paths to access models and preprocessing
- Imports CSRNet model
- Verifies all required paths exist
- Points to `ml/src/` as project root

**Expected output:**

```
✅ CSRNet imported successfully
📁 Project paths configured...
```

### Cell 3: Load Model Checkpoint ✅

**What it does:**

- Loads CSRNet model from `ml/checkpoints/csrnet.pth`
- Uses the `load_csrnet()` helper function
- Displays model architecture info

**Expected output:**

```
📦 Loading CSRNet model...
✅ Model loaded successfully
   - Frontend: 26 parameter tensors
   - Backend: 14 parameter tensors
```

### Cell 4: Load Real Crowd Image ✅

**What it does:**

- Scans `ml/datasets/images/` for test images
- Lists all available images (jpg, png, etc.)
- Loads the first image
- Applies manual preprocessing (ToTensor + ImageNet normalization)
- Shows model statistics (16.2M parameters)

**Expected output:**

```
📂 Looking for images...
🖼️  Found 3 images:
   1. 360_F_216678910_...jpg
   2. 360_F_600734899_...jpg
   3. png-multicultural-crowd...jpg
➡️  Using: 360_F_216678910_...jpg
```

### Cell 5: Run Inference ✅

**What it does:**

- Runs CSRNet model on the loaded image
- Generates density map
- Calculates crowd count
- Displays results prominently

**Expected output:**

```
🧠 Running inference...
✅ INFERENCE SUCCESSFUL!
==================================================
   🎯 FINAL COUNT: 42 people
==================================================
```

### Cell 6: Summary (Markdown)

- Overview of what was successfully tested
- Next steps and recommendations

### Cell 7: Preprocessing Module Section (Markdown)

- Introduces the CSRNetPreprocessor module

### Cell 8: Import Preprocessor ✅

**What it does:**

- Imports the proper `CSRNetPreprocessor` class
- Initializes it with correct settings
- Shows it uses the same preprocessing as original CSRNet paper

**Expected output:**

```
✅ CSRNetPreprocessor initialized
   - No resizing (fully convolutional)
   - ToTensor + ImageNet normalization
   - Output downsampled by factor of 8
```

### Cell 9: Test with Preprocessor ✅

**What it does:**

- Runs the SAME image through CSRNetPreprocessor
- Compares results with manual preprocessing
- Shows they should produce identical results

**Expected output:**

```
📊 Results with proper preprocessing:
   Raw count: 42.31
   Rounded: 42
```

### Cell 10-15: DEBUG Section 🔍

**What it does:**

- Diagnostic cells to analyze checkpoint issues
- Checks checkpoint structure
- Examines loaded weights
- Analyzes density map output
- Provides troubleshooting guidance

**Use when:**

- Model produces wrong counts
- Checkpoint won't load
- Results don't match expectations
- Debugging architecture mismatches

---

## ✅ What Gets Tested

1. ✅ **Model Architecture**: Verifies CSRNet loads correctly
2. ✅ **Checkpoint Loading**: Ensures weights load from `.pth` file
3. ✅ **Image Loading**: Tests with real crowd images from dataset
4. ✅ **Preprocessing**: Both manual and module-based approaches
5. ✅ **Inference**: Full forward pass through the network
6. ✅ **Density Map**: Output shape and value validation
7. ✅ **Count Calculation**: Sum of density map for final count

---

## 🎯 Expected Workflow

### Quick Test (Cells 1-5):

1. Run cell 2 → Import model
2. Run cell 3 → Load checkpoint
3. Run cell 4 → Load test image
4. Run cell 5 → Get crowd count
5. ✅ Done! Model is working.

### Full Test with Preprocessor (Cells 1-9):

1-5. Same as above 6. Run cell 8 → Import CSRNetPreprocessor 7. Run cell 9 → Compare preprocessing approaches 8. ✅ Verify both methods give same results

### Debug Mode (Cells 1-15):

- Run all cells when troubleshooting issues
- Cells 11-15 provide detailed diagnostics
- Follow the recommendations in cell 16

---

## 📊 Key Requirements

### Files Needed:

- ✅ `ml/src/models/csrnet/csrnet.py` - Model definition
- ✅ `ml/src/preprocessing/csrnet_preprocess.py` - Preprocessor
- ✅ `ml/checkpoints/csrnet.pth` - Model weights
- ✅ `ml/datasets/images/*.jpg` - Test images (at least 1)

### Python Packages:

- `torch`
- `torchvision`
- `PIL (Pillow)`
- `numpy`

---

## 🚨 Common Issues & Solutions

### Issue: "No module named 'models.csrnet'"

**Solution:** Make sure you're running from `ml/src/utils/` directory

### Issue: "FileNotFoundError: csrnet.pth"

**Solution:** Verify checkpoint exists at `ml/checkpoints/csrnet.pth`

### Issue: "No images found in datasets/images"

**Solution:** Add at least one crowd image to `ml/datasets/images/`

### Issue: "Count is way too high/low"

**Solution:** Run cells 11-15 for diagnostics, check if checkpoint is properly trained

### Issue: "Cannot import CSRNetPreprocessor"

**Solution:** Ensure `ml/src/preprocessing/csrnet_preprocess.py` exists

---

## 🎓 Learning Points

This notebook demonstrates:

- ✅ How to load PyTorch models with checkpoints
- ✅ Proper image preprocessing for CNNs
- ✅ Running inference on custom images
- ✅ Interpreting density maps for counting
- ✅ Debugging model issues systematically
- ✅ Using both manual and modular preprocessing

---

## 📝 Next Steps After Running

1. **If model works well:**

   - Deploy via API (`backend/app/api/v1/endpoints/csrnet.py`)
   - Test webcam app
   - Try multiple test images

2. **If counts are wrong:**

   - Run diagnostic cells (11-15)
   - Check if checkpoint is properly trained
   - Consider getting official pre-trained weights
   - Test with ShanghaiTech dataset images

3. **For production:**
   - Always use `CSRNetPreprocessor` for consistency
   - Add error handling
   - Log predictions for monitoring
   - Validate inputs before inference

---

## 🎯 Success Criteria

The notebook is working correctly when:

- ✅ All cells run without errors
- ✅ Model loads successfully
- ✅ Test image is found and loaded
- ✅ Inference completes and produces a count
- ✅ Both preprocessing methods give similar results
- ✅ Counts are reasonable for the test images

---

**Last Updated:** January 2025
**Status:** ✅ Ready to use
**Maintained by:** Crowd Flow Prediction Analyzer Team
