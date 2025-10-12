"""
Check GPU memory before training
"""
import torch

print("=" * 60)
print("GPU Memory Status")
print("=" * 60)

if torch.cuda.is_available():
    device = torch.device('cuda')
    print(f"Device: {torch.cuda.get_device_name(0)}")
    
    # Total memory
    total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"Total VRAM: {total:.2f} GB")
    
    # Current allocation
    allocated = torch.cuda.memory_allocated(0) / (1024**3)
    reserved = torch.cuda.memory_reserved(0) / (1024**3)
    
    print(f"Allocated: {allocated:.3f} GB")
    print(f"Reserved:  {reserved:.3f} GB")
    print(f"Free:      {total - reserved:.3f} GB")
    
    print("\n" + "=" * 60)
    print("Recommendation for RTX 3050 6GB:")
    print("  batch_size = 1  → ~2.0 GB peak (SAFEST)")
    print("  batch_size = 2  → ~3.5 GB peak (SAFE)")
    print("  batch_size = 3  → ~4.5 GB peak (OPTIMAL) ✓")
    print("  batch_size = 4  → ~6.0 GB peak (OOM)")
    print("=" * 60)
else:
    print("CUDA not available!")
