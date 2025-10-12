# Batch Size Comparison for RTX 3050 6GB

## Performance vs Safety Trade-off

| Batch Size | VRAM Usage  | Speed/Batch | Batches/Epoch | Time/Epoch | Total (100 epochs) | Risk Level     |
| ---------- | ----------- | ----------- | ------------- | ---------- | ------------------ | -------------- |
| 1          | ~2.0 GB     | 12s         | 300           | 60 min     | **4-5 days**       | 🟢 SAFEST      |
| 2          | ~3.5 GB     | 14s         | 150           | 35 min     | **2-3 days**       | 🟢 SAFE        |
| **3**      | **~4.5 GB** | **16s**     | **100**       | **27 min** | **~2 days**        | 🟡 **OPTIMAL** |
| 4          | ~6.0 GB     | 18s         | 75            | 22 min     | 1.5 days           | 🔴 OOM!        |

## Why batch_size=3 is the sweet spot:

### ✅ Advantages:

1. **3× faster than batch_size=1** (100 vs 300 batches per epoch)
2. **Leaves ~1.5GB VRAM headroom** (4.5GB used out of 6GB)
3. **Better gradient estimates** (more samples per update)
4. **Reasonable training time** (~2 days for 100 epochs)

### ⚠️ Considerations:

1. **Slightly higher OOM risk** than batch_size=1 or 2
2. **Variable image sizes** might spike memory occasionally
3. **System processes** can steal VRAM unexpectedly

## Memory Safety Tips with batch_size=3:

1. **Close other GPU apps** (Chrome GPU acceleration, Discord, etc.)
2. **Monitor first 10 batches** closely:
   ```cmd
   nvidia-smi -l 1
   ```
3. **If OOM occurs**: The training script will crash, just reduce to batch_size=2 and restart

## What to Watch For:

### ✅ Good signs (training will complete):

```
Epoch 1: 10% | 10/100 [02:40<24:00, 16.0s/it, loss=0.01, mae=200]
```

- Memory stable across batches
- No warning messages
- Progress bar advances smoothly

### 🔴 Bad signs (reduce batch size):

```
Epoch 1: 5% | 5/100 [01:20<25:20, 16.0s/it, loss=0.01, mae=200]
RuntimeError: CUDA out of memory
```

- OOM crashes
- Memory warnings in logs

## Fallback Plan:

If OOM happens with batch_size=3:

1. **Edit** `ml/csrnet_config.yaml`:

   ```yaml
   batch_size: 2 # or 1 if very conservative
   ```

2. **Restart training** - it will resume from last checkpoint if you had any saves

## Bottom Line:

**Start with batch_size=3** ✓

- Good balance of speed and safety
- Should work fine on RTX 3050 6GB
- If it crashes, just drop to 2 and restart

---

**Current config is set to batch_size=3** 🚀
Ready to train!
