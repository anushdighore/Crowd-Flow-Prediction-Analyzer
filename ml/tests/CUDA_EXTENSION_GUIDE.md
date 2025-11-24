# CUDA Extension Testing Notebook Guide

## 📓 Notebook: `7-cuda-extension-check.ipynb`

**Location:** `ml/src/utils/7-cuda-extension-check.ipynb`

---

## 🎯 Purpose

This notebook is your **complete diagnostic tool** for CUDA and PyTorch environment issues. It helps you:

- ✅ Verify CUDA availability
- ✅ Test GPU functionality
- ✅ Check compiler setup
- ✅ Diagnose extension issues
- ✅ Get clear recommendations

---

## 📋 What It Checks

### 1. **Environment Basics**

- Python version
- PyTorch installation
- Platform information

### 2. **CUDA Status**

- CUDA availability
- GPU detection
- CUDA version
- cuDNN version
- GPU memory

### 3. **GPU Performance**

- Matrix multiplication benchmark
- CPU vs GPU speedup
- Result verification

### 4. **C++ Compiler**

- Compiler detection (MSVC, GCC, Clang)
- Compiler version
- PATH configuration

### 5. **CUDA Extensions**

- mamba-ssm installation
- causal-conv1d
- Triton
- Other optional packages

### 6. **Model Testing**

- CSRNet loading
- TMTB/VMamba loading
- Inference tests
- Error diagnosis

### 7. **Extension Compilation**

- Test compilation (advanced)
- Verify toolchain
- Performance check

### 8. **Summary & Recommendations**

- Configuration status
- Performance expectations
- Next steps

---

## 🔢 Cell-by-Cell Breakdown

| Cell # | Type     | Purpose                    | Expected Time |
| ------ | -------- | -------------------------- | ------------- |
| 1      | Markdown | Introduction               | -             |
| 2      | Markdown | Section: Environment       | -             |
| 3      | Code     | Python & PyTorch version   | < 1s          |
| 4      | Markdown | Section: CUDA              | -             |
| 5      | Code     | CUDA availability check    | < 1s          |
| 6      | Markdown | Section: Operations        | -             |
| 7      | Code     | Test CUDA ops (benchmark)  | ~5s           |
| 8      | Markdown | Section: Compiler          | -             |
| 9      | Code     | C++ compiler check         | ~5s           |
| 10     | Markdown | Section: Packages          | -             |
| 11     | Code     | Check CUDA packages        | < 1s          |
| 12     | Markdown | Section: CSRNet            | -             |
| 13     | Code     | Test CSRNet loading        | ~10s          |
| 14     | Markdown | Section: TMTB              | -             |
| 15     | Code     | Test TMTB loading          | ~20s          |
| 16     | Markdown | Section: Compilation       | -             |
| 17     | Code     | Test extension compilation | 1-2 min       |
| 18     | Markdown | Section: Summary           | -             |
| 19     | Code     | Generate recommendations   | < 1s          |
| 20     | Markdown | Troubleshooting guide      | -             |

**Total Runtime:** 2-3 minutes (skip cell 17 for faster check)

---

## 🎯 Usage Scenarios

### Scenario 1: First Time Setup

**When:** Just installed PyTorch, not sure if CUDA works
**What to do:** Run cells 1-11
**Expected outcome:** Know if CUDA is available and working

### Scenario 2: Model Won't Load

**When:** Getting errors loading CSRNet or TMTB
**What to do:** Run cells 12-15
**Expected outcome:** Identify specific loading issues

### Scenario 3: Extension Problems

**When:** Errors about "mamba-ssm" or CUDA extensions
**What to do:** Run cells 10-11, 16-17
**Expected outcome:** Understand extension requirements

### Scenario 4: Performance Issues

**When:** Models are slow or not using GPU
**What to do:** Run cells 5-7
**Expected outcome:** Verify GPU acceleration

### Scenario 5: Complete Diagnostic

**When:** Setting up new machine or troubleshooting
**What to do:** Run all cells
**Expected outcome:** Full environment report

---

## ✅ Interpreting Results

### Good Configuration ✅

```
CUDA available: ✅ YES
C++ Compiler: ✅ Found
CSRNet: ✅ Loaded
TMTB: ✅ Loaded
GPU speedup: 10-50x
```

**Action:** You're all set! Proceed with model testing.

### CPU-Only Configuration ⚠️

```
CUDA available: ❌ NO
C++ Compiler: ✅ Found
CSRNet: ✅ Loaded (CPU)
TMTB: ✅ Loaded (CPU)
```

**Action:** Models work but slower. Consider GPU if available.

### Missing Compiler ⚠️

```
CUDA available: ✅ YES
C++ Compiler: ❌ Not found
CSRNet: ✅ Loaded
TMTB: ⚠️ May fail with extensions
```

**Action:** Install C++ compiler for full functionality.

### Extension Issues ⚠️

```
CUDA available: ✅ YES
mamba-ssm: ❌ Not installed
TMTB: ⚠️ Using fallback
```

**Action:** This is OK! Fallbacks work fine.

---

## 🚨 Common Issues & Solutions

### Issue 1: "RuntimeError: CUDA out of memory"

**Cause:** GPU memory exhausted
**Solutions:**

1. Reduce batch size
2. Use smaller images
3. Clear GPU cache: `torch.cuda.empty_cache()`
4. Restart kernel
5. Switch to CPU

### Issue 2: "ImportError: No module named 'mamba_ssm'"

**Cause:** Optional CUDA extension not installed
**Solutions:**

1. This is FINE - model will use fallback
2. Optional install: `pip install mamba-ssm`
3. Requires C++ compiler + CUDA toolkit

### Issue 3: "torch.cuda.is_available() returns False"

**Cause:** CUDA not properly configured
**Solutions:**

1. Check GPU: Run `nvidia-smi` in terminal
2. Install NVIDIA drivers
3. Reinstall PyTorch with CUDA:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

### Issue 4: "No C++ compiler found"

**Cause:** Build tools not installed
**Solutions:**

- **Windows:** Install Visual Studio Build Tools
  - Download from https://visualstudio.microsoft.com/downloads/
  - Select "Desktop development with C++"
- **Linux:**
  ```bash
  sudo apt install build-essential  # Ubuntu/Debian
  sudo yum groupinstall "Development Tools"  # CentOS
  ```
- **macOS:**
  ```bash
  xcode-select --install
  ```

### Issue 5: "Compilation failed: nvcc not found"

**Cause:** CUDA toolkit not in PATH
**Solutions:**

1. Install CUDA Toolkit from NVIDIA
2. Add to PATH:
   - Windows: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin`
   - Linux: `/usr/local/cuda/bin`
3. Verify: `nvcc --version`

### Issue 6: "Model loading takes forever"

**Cause:** Large checkpoint, slow disk, or first-time compilation
**Solutions:**

1. Wait patiently (first load is slow)
2. Subsequent loads are faster
3. Use SSD if available
4. Check disk space

---

## 📊 Performance Benchmarks

### Expected GPU Speedup (1000x1000 matrix multiplication):

- **Good:** 10-20x faster than CPU
- **Great:** 20-50x faster than CPU
- **Excellent:** 50-100x+ faster than CPU
- **Problem:** < 5x speedup (check drivers)

### Expected Model Inference Times (512x512 image):

| Model  | GPU (with CUDA) | GPU (no extensions) | CPU   |
| ------ | --------------- | ------------------- | ----- |
| CSRNet | ~0.1s           | ~0.1s (same)        | ~0.5s |
| TMTB   | ~0.3s           | ~0.5s               | ~2-3s |
| MCNN   | ~0.08s          | ~0.08s (same)       | ~0.3s |

---

## 💡 Understanding CUDA Extensions

### What are CUDA Extensions?

- Custom C++/CUDA code compiled for your GPU
- Provide 2-3x speedup for specific operations
- Used by mamba-ssm, selective_scan, etc.

### Do I Need Them?

**NO!** Models have pure PyTorch fallbacks.

### When to Install:

✅ **Install if:**

- Have GPU + C++ compiler
- Need maximum performance
- Working with video/real-time
- Training models

❌ **Don't bother if:**

- Running on CPU only
- No C++ compiler
- Current performance acceptable
- Just testing/development

### How to Install:

```bash
# Requires: CUDA toolkit + C++ compiler
pip install mamba-ssm causal-conv1d

# May take 5-10 minutes to compile
# Watch for compilation errors
```

---

## 🎓 Technical Details

### CUDA Architecture Check:

```python
props = torch.cuda.get_device_properties(0)
print(f"Compute Capability: {props.major}.{props.minor}")
```

**Meaning:**

- 3.5-5.x: Older GPUs (Kepler, Maxwell)
- 6.x: Pascal (GTX 10 series)
- 7.x: Volta/Turing (RTX 20 series)
- 8.x: Ampere (RTX 30 series)
- 9.x: Hopper (RTX 40 series)

**Minimum for CUDA extensions:** Usually 6.0+

### Memory Management:

```python
torch.cuda.empty_cache()  # Clear unused memory
torch.cuda.reset_peak_memory_stats()  # Reset counters
torch.cuda.memory_summary()  # Detailed info
```

### Mixed Precision (Speed Optimization):

```python
with torch.cuda.amp.autocast():
    output = model(input)
```

Can provide 2x speedup with minimal accuracy loss.

---

## 🔄 Workflow After Diagnostics

### If Everything Works ✅

1. Run `5-csrnet-check.ipynb` to test CSRNet
2. Run `6-tmtb-check.ipynb` to test TMTB
3. Compare performance and accuracy
4. Deploy chosen model(s)

### If CUDA Not Available ⚠️

1. ✅ CSRNet works great on CPU
2. ⚠️ TMTB slow on CPU (use CSRNet instead)
3. Consider cloud GPU (Colab, AWS, etc.)
4. Or proceed with CPU for development

### If Extensions Fail ⚠️

1. ✅ Don't worry - fallbacks work
2. Models run ~20% slower (still acceptable)
3. Optional: troubleshoot compiler setup
4. Or ignore and use PyTorch-native

### If Models Won't Load ❌

1. Check checkpoint paths
2. Verify file integrity
3. Check disk space
4. Review error messages in diagnostic
5. Try re-downloading checkpoints

---

## 📚 Additional Resources

### PyTorch CUDA Setup:

- https://pytorch.org/get-started/locally/
- https://pytorch.org/docs/stable/cuda.html

### NVIDIA Drivers:

- https://www.nvidia.com/Download/index.aspx
- https://developer.nvidia.com/cuda-toolkit

### Compiler Setup:

- **Windows:** https://visualstudio.microsoft.com/downloads/
- **Linux:** https://gcc.gnu.org/
- **macOS:** https://developer.apple.com/xcode/

### CUDA Extensions:

- mamba-ssm: https://github.com/state-spaces/mamba
- Triton: https://github.com/openai/triton

---

## 🎯 Quick Decision Tree

```
Start Here
    │
    ├─ Have NVIDIA GPU?
    │   ├─ YES → Run cells 3-7
    │   │         └─ CUDA works? → ✅ Use GPU!
    │   │         └─ CUDA fails? → Fix drivers/PyTorch
    │   │
    │   └─ NO → ✅ Use CPU (CSRNet recommended)
    │
    ├─ Models won't load?
    │   └─ Run cells 12-15 → Check errors
    │
    ├─ Extensions failing?
    │   └─ Run cells 10-11, 16-17
    │       ├─ Have compiler? → Can fix
    │       └─ No compiler? → Use fallbacks ✅
    │
    └─ Just checking setup?
        └─ Run all cells → Get full report
```

---

**Created:** January 2025  
**Status:** ✅ Production Ready  
**Use When:** Setting up new environment, troubleshooting, or performance issues
