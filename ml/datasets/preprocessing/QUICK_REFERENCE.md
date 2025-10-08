# CSRNet Preprocessing - Quick Reference

## ❌ WRONG (Don't Do This)

```python
transform = transforms.Compose([
    transforms.Resize((512, 512)),  # <-- NO!
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```

## ✅ CORRECT (Do This)

```python
from preprocessing import CSRNetPreprocessor

preprocessor = CSRNetPreprocessor()
tensor = preprocessor.preprocess(pil_image)
```

## 📐 Size Relationship

```
Input:  1024×768  →  Output: 128×96  (÷8)
Input:  512×512   →  Output: 64×64   (÷8)
Input:  1920×1080 →  Output: 240×135 (÷8)
```

## 🧪 Quick Test

```bash
python test_preprocessing.py
```

## 📖 Full Documentation

- `preprocessing/README.md` - Technical details
- `PREPROCESSING_FIX.md` - Problem analysis
- `PREPROCESSING_COMPLETE.md` - Complete summary

## 🎯 Expected Behavior

- Random images → Meaningless results (normal!)
- Real crowd images → Accurate counts (±10%)
- Single person → 1-3 count (acceptable range)

## 🚨 If Still Wrong

1. Check model weights (`csrnet.pth`)
2. Use real crowd images (not random noise)
3. Verify image upload isn't corrupting data
4. Check logs for loading errors
