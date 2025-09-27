import torch
ckpt = torch.load("jhu_5.pth", map_location="cpu")  
total = sum(p.numel() for p in ckpt.values() if torch.is_tensor(p))
print(f"Actual checkpoint: {total:,} parameters")
