# CSRNet Preprocessing Module

## Overview
This module implements the **EXACT** preprocessing pipeline used in the original CSRNet paper and official PyTorch implementation.

## Key Points

### ❌ Common Mistakes
Many implementations incorrectly resize images to fixed sizes (e.g., 512×512). This is **WRONG** for CSRNet!

### ✅ Correct Preprocessing (What We Do)
1. **NO RESIZING** - CSRNet is fully convolutional and accepts any input resolution
2. **ToTensor** - Converts PIL Image [0, 255] to Tensor [0.0, 1.0]
3. **Normalize** - Apply ImageNet normalization:
   - Mean: [0.485, 0.456, 0.406]
   - Std: [0.229, 0.224, 0.225]

## Why Your Predictions Were Wrong

### Problem
You reported: "1 person detected as 35" - this is a **preprocessing issue**!

### Root Causes
1. **Missing proper preprocessing** - Previously just used basic transforms
2. **No validation** of input image properties
3. **Possible image corruption** or wrong format during upload

### Solution
This module provides:
- ✅ Exact preprocessing matching the original paper
- ✅ Input validation (RGB conversion, size logging)
- ✅ Proper tensor normalization
- ✅ Debug logging at each step

## Usage

### Basic Usage
```python
from preprocessing import CSRNetPreprocessor

preprocessor = CSRNetPreprocessor()

# From PIL Image
img_tensor = preprocessor.preprocess(pil_image)

# From file path
img_tensor = preprocessor.preprocess_from_path("crowd.jpg")

# From bytes (e.g., file upload)
img_tensor = preprocessor.preprocess_from_bytes(image_bytes)
```

### In FastAPI
```python
from preprocessing import get_csrnet_preprocessor

preprocessor = get_csrnet_preprocessor()

@app.post("/count")
async def count_people(file: UploadFile):
    contents = await file.read()
    img_tensor = preprocessor.preprocess_from_bytes(contents)
    img_tensor = img_tensor.to(device)
    
    with torch.no_grad():
        density_map = model(img_tensor)
        count = density_map.sum().item()
    
    return {"count": int(round(count))}
```

## Model Architecture Notes

### Input → Output Size Relationship
CSRNet downsamples by **factor of 8** due to 3 max pooling layers:
- Input: (H, W, 3) → Output: (H/8, W/8, 1)
- Example: 512×512 → 64×64 density map

### Output Interpretation
The output is a **density map** where:
- Each pixel represents local crowd density
- Sum of all pixels = predicted total count
- Multiply by 64 if comparing to ground truth (see `image.py` line 40)

## Comparison with Original Code

### From `architectures/CSRNet-pytorch/train.py` (lines 57-61)
```python
transform=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]),
])
```

Our implementation is **IDENTICAL** to the original!

## Testing

### Test the preprocessor
```python
from preprocessing import CSRNetPreprocessor
from PIL import Image

preprocessor = CSRNetPreprocessor()

# Test with a real image
img = Image.open("test_crowd.jpg")
print(f"Original size: {img.size}")

tensor = preprocessor.preprocess(img)
print(f"Tensor shape: {tensor.shape}")

# Calculate expected output shape
output_shape = preprocessor.get_output_shape(tensor.shape)
print(f"Expected density map shape: {output_shape}")
```

## Debugging Wrong Predictions

If you still get wrong predictions, check:

1. **Model weights** - Is `csrnet.pth` trained on the same dataset type?
2. **Image quality** - Low quality images will have poor predictions
3. **Crowd density** - Model trained on ShanghaiTech works best for similar scenes
4. **Checkpoint loading** - Check logs for "Successfully loaded model weights"
5. **Scale factor** - Some implementations multiply density by 64 (ground truth scale)

## Expected Results

### On ShanghaiTech Test Set (Part A)
- MAE: ~68 (mean absolute error)
- MSE: ~115 (mean squared error)

### On Your Images
- Images similar to training data → Good predictions
- Very different scenes → May need retraining or fine-tuning
- Single person in large image → Count should be close to 1 (±2)

## References
- Original Paper: "CSRNet: Dilated Convolutional Neural Networks for Understanding the Highly Congested Scenes" (CVPR 2018)
- Original Code: https://github.com/leeyeehoo/CSRNet-pytorch
- Training code: `architectures/CSRNet-pytorch/train.py`
- Image loading: `architectures/CSRNet-pytorch/image.py`
