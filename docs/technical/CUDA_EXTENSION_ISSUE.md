# CUDA Selective Scan Extension Issue

## Problem Summary

The VMamba-TMTB model requires CUDA selective scan kernels for inference, but none are currently installed:

- ❌ `selective_scan_cuda_oflex` - Not available
- ❌ `selective_scan_cuda_core` - Not available
- ❌ `selective_scan_cuda` - Not available
- ❌ `mamba_ssm` - Not available

## Error Details

```
NameError: name 'selective_scan_cuda_oflex' is not defined
```

The model uses `forward_type="v3noz"` which is configured to use `SelectiveScanOflex`, requiring the `selective_scan_cuda_oflex` compiled CUDA extension.

## Solution Options

### Option 1: Install mamba-ssm (Recommended)

Install the official Mamba package which includes pre-compiled CUDA kernels:

```bash
conda activate crowdenv
pip install mamba-ssm
```

**Pros:**

- Official implementation
- Pre-compiled binaries (if available for your CUDA version)
- Most likely to work correctly

**Cons:**

- Requires compatible CUDA version (11.8+ typically)
- May need compilation if no pre-built wheels available
- Installation can be complex

### Option 2: Install causal-conv1d + mamba-ssm

Some versions need the causal-conv1d dependency first:

```bash
conda activate crowdenv
pip install causal-conv1d>=1.1.0
pip install mamba-ssm
```

### Option 3: Compile Selective Scan Extensions from Source

The VMamba repository should include the CUDA extensions. Compile them:

```bash
cd architectures/taste_more_taste_better/kernels/selective_scan
python setup.py install
```

**Requirements:**

- NVIDIA GPU with CUDA support
- CUDA toolkit installed (nvcc compiler)
- PyTorch with CUDA support
- Compatible GCC/MSVC compiler

### Option 4: Use CPU Fallback (Not Recommended)

Modify the model to use PyTorch-only selective scan (very slow, may not exist for all variants):

1. Change forward_type in model config from "v3noz" to "v01" or "v02"
2. This uses `SelectiveScanMamba` which might have a CPU fallback

**Pros:**

- No compilation needed
- Works without GPU

**Cons:**

- Extremely slow (10-100x slower)
- May not be fully implemented
- Not tested/supported

### Option 5: Use Pre-trained Model with Different Architecture

Switch to a model that doesn't require selective scan:

- Use a standard CNN-based crowd counter
- Use transformer-based model
- Use older VMamba version with full PyTorch support

## Current Environment

**System:**

- OS: Windows
- Python: 3.9.23
- Conda env: crowdenv
- PyTorch: 2.1.2+cu121 (CUDA 12.1)
- CUDA available: Yes

**Model:**

- Architecture: VMamba-TMTB (MAMBA4CC)
- Forward type: v3noz
- Selective Scan: SelectiveScanOflex (requires CUDA)
- Parameters: 88,683,529 (loaded successfully)

## Recommended Action

**Try Option 1 first:**

1. Activate environment: `conda activate crowdenv`
2. Install mamba-ssm: `pip install mamba-ssm`
3. Test import: `python -c "import selective_scan_cuda; print('Success!')"`
4. Re-run inference test

If Option 1 fails with compilation errors, try Option 2 (install causal-conv1d first).

## Testing After Installation

Run this in the `backend_api_tests.ipynb` notebook:

```python
# Test imports
try:
    import selective_scan_cuda_oflex
    print("✅ selective_scan_cuda_oflex available")
except:
    print("❌ selective_scan_cuda_oflex not available")

# Test inference
with torch.no_grad():
    dummy_input = torch.randn(1, 3, 384, 512).to(device)
    outputs = model(dummy_input)
    print(f"✅ Inference successful! Output shape: {outputs[0].shape}")
```

## Alternative: Use CPU-Only Mode

If CUDA extensions cannot be installed, we can modify the loader to force CPU mode with PyTorch fallbacks, but this is **NOT recommended** for production use due to extreme performance degradation.

## References

- Mamba SSM: https://github.com/state-spaces/mamba
- VMamba: https://github.com/MzeroMiko/VMamba
- Selective Scan explanation: https://arxiv.org/abs/2312.00752
