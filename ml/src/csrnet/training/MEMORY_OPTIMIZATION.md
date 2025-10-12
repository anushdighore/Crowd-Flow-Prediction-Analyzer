# CSRNet Memory Optimization Guide for RTX 3050 6GB

## Current Issue

Your RTX 3050 has 6GB VRAM. CSRNet with batch_size=4 caused OOM after 6 batches during backpropagation.

## Solutions Implemented

### 1. Reduced Batch Size ✓

**Changed: `batch_size: 4 → 1`**

- Location: `ml/csrnet_config.yaml`
- This will use ~1.5GB per batch instead of ~6GB
- Training will be slower but stable

### 2. Optional: Test batch_size=2

After confirming batch_size=1 works, you can try:

```yaml
batch_size: 2 # ~3GB VRAM usage
```

## Memory Breakdown (Approximate)

| Component          | Memory Usage |
| ------------------ | ------------ |
| Model weights      | ~62 MB       |
| Optimizer state    | ~124 MB      |
| Per-batch (size=1) | ~1.5 GB      |
| Per-batch (size=2) | ~3.0 GB      |
| Per-batch (size=4) | ~6.0 GB      |

## What to Expect

### With batch_size=1:

- **VRAM usage**: ~2 GB peak
- **Training speed**: ~12-15s per batch
- **Epochs to complete**: ~100 epochs × 300 batches = ~10-12 hours

### With batch_size=2 (if you try):

- **VRAM usage**: ~3.5 GB peak
- **Training speed**: ~15-18s per batch
- **Epochs to complete**: ~100 epochs × 150 batches = ~6-8 hours

## Monitor During Training

Watch for:

```
nvidia-smi
```

- Memory usage should stay below 5.5 GB
- If OOM still occurs with batch_size=1, reduce num_workers to 0

## Next Steps

1. ✓ Config updated to batch_size=1
2. Run training again via menu option [3]
3. Monitor first few batches to confirm stability
4. Optional: After 1 epoch, try batch_size=2 if you want faster training
