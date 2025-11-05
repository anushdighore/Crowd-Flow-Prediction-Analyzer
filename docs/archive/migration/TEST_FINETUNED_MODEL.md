# Testing Your Fine-tuned VMamba Model

## 🧪 Quick Test Script

### test_finetuned.py

```python
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from models.vmamba_tmtb import VMambaTMTB


def load_finetuned_model(checkpoint_path, device='cuda'):
    """Load fine-tuned VMamba model"""
    model = VMambaTMTB()

    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()

    print(f"✅ Loaded model from: {checkpoint_path}")
    if 'best_mae' in checkpoint:
        print(f"   Best MAE: {checkpoint['best_mae']:.2f}")
    if 'epoch' in checkpoint:
        print(f"   Epoch: {checkpoint['epoch']}")

    return model


def predict_count(model, image_path, device='cuda', visualize=True):
    """Predict crowd count from image"""

    # Load and preprocess image
    img = Image.open(image_path).convert('RGB')

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])

    img_tensor = transform(img).unsqueeze(0).to(device)

    # Predict
    with torch.no_grad():
        density_map = model(img_tensor)

    # Calculate count
    count = density_map.sum().item()

    # Visualize
    if visualize:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Original image
        axes[0].imshow(img)
        axes[0].set_title('Original Image')
        axes[0].axis('off')

        # Density map
        density_np = density_map[0, 0].cpu().numpy()
        axes[1].imshow(density_np, cmap='jet')
        axes[1].set_title(f'Density Map\nPredicted Count: {count:.1f}')
        axes[1].axis('off')

        # Overlay
        axes[2].imshow(img)
        axes[2].imshow(density_np, cmap='jet', alpha=0.5)
        axes[2].set_title('Overlay')
        axes[2].axis('off')

        plt.tight_layout()
        plt.show()

    return count, density_map


def batch_test(model, test_dir, device='cuda'):
    """Test on multiple images"""

    import glob
    image_paths = glob.glob(os.path.join(test_dir, '*.jpg'))

    print(f"\n🔍 Testing on {len(image_paths)} images...")

    results = []
    for img_path in image_paths:
        count, _ = predict_count(model, img_path, device, visualize=False)
        results.append({
            'image': os.path.basename(img_path),
            'count': count
        })
        print(f"   {os.path.basename(img_path)}: {count:.1f} people")

    return results


def compare_models(checkpoint1, checkpoint2, test_image, device='cuda'):
    """Compare two model checkpoints"""

    print("Loading Model 1...")
    model1 = load_finetuned_model(checkpoint1, device)

    print("\nLoading Model 2...")
    model2 = load_finetuned_model(checkpoint2, device)

    # Load image
    img = Image.open(test_image).convert('RGB')
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    img_tensor = transform(img).unsqueeze(0).to(device)

    # Predict with both models
    with torch.no_grad():
        density1 = model1(img_tensor)
        density2 = model2(img_tensor)

    count1 = density1.sum().item()
    count2 = density2.sum().item()

    # Visualize comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(img)
    axes[0].set_title('Original Image')
    axes[0].axis('off')

    axes[1].imshow(density1[0, 0].cpu().numpy(), cmap='jet')
    axes[1].set_title(f'Model 1: {count1:.1f} people')
    axes[1].axis('off')

    axes[2].imshow(density2[0, 0].cpu().numpy(), cmap='jet')
    axes[2].set_title(f'Model 2: {count2:.1f} people')
    axes[2].axis('off')

    plt.tight_layout()
    plt.show()

    print(f"\n📊 Comparison:")
    print(f"   Model 1: {count1:.1f} people")
    print(f"   Model 2: {count2:.1f} people")
    print(f"   Difference: {abs(count1 - count2):.1f}")

    return count1, count2


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test fine-tuned VMamba model')
    parser.add_argument('--checkpoint', required=True,
                       help='Path to fine-tuned checkpoint')
    parser.add_argument('--image', required=True,
                       help='Path to test image or directory')
    parser.add_argument('--device', default='cuda',
                       help='Device (cuda or cpu)')
    parser.add_argument('--compare', default=None,
                       help='Second checkpoint to compare')

    args = parser.parse_args()

    # Check device
    if args.device == 'cuda' and not torch.cuda.is_available():
        print("⚠️  CUDA not available, using CPU")
        args.device = 'cpu'

    # Load model
    model = load_finetuned_model(args.checkpoint, args.device)

    # Test
    if os.path.isdir(args.image):
        # Batch test
        results = batch_test(model, args.image, args.device)
    elif args.compare:
        # Compare two models
        compare_models(args.checkpoint, args.compare, args.image, args.device)
    else:
        # Single image test
        count, _ = predict_count(model, args.image, args.device, visualize=True)
        print(f"\n🎯 Predicted count: {count:.1f} people")
```

---

## 🎯 Usage Examples

### 1. Test on Single Image

```bash
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image test_image.jpg
```

This will show:

- Original image
- Density map
- Overlay visualization
- Predicted count

---

### 2. Batch Test on Directory

```bash
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image datasets/ShanghaiTech/part_A/test_data/images/
```

This will test all images in the directory and print counts.

---

### 3. Compare Two Checkpoints

```bash
# Compare best model vs final model
python test_finetuned.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --compare checkpoints/vmamba_finetuned/vmamba_shanghai_final.pth \
    --image test_image.jpg
```

This shows side-by-side comparison.

---

### 4. Compare Before/After Fine-tuning

```bash
# Original JHU checkpoint vs fine-tuned
python test_finetuned.py \
    --checkpoint checkpoints/jhu_5.pth \
    --compare checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --image test_image.jpg
```

---

## 📊 Evaluate on Test Set

### evaluate_testset.py

```python
import torch
import h5py
import numpy as np
from tqdm import tqdm
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from finetune_vmamba import create_dataloaders, load_finetuned_model


def evaluate_testset(checkpoint_path, data_root, device='cuda'):
    """Evaluate model on test set"""

    print(f"Loading model from: {checkpoint_path}")
    model = load_finetuned_model(checkpoint_path, device)

    print(f"Loading test data from: {data_root}")
    _, test_loader = create_dataloaders(data_root, batch_size=1, num_workers=4)

    print(f"\n🧪 Evaluating on {len(test_loader)} images...")

    model.eval()
    all_mae = []
    all_mse = []
    all_counts = []
    all_preds = []

    with torch.no_grad():
        for images, targets, counts in tqdm(test_loader):
            images = images.to(device)
            counts = counts[0].item()  # Ground truth count

            # Predict
            outputs = model(images)
            pred_count = outputs.sum().item()

            # Calculate errors
            mae = abs(pred_count - counts)
            mse = (pred_count - counts) ** 2

            all_mae.append(mae)
            all_mse.append(mse)
            all_counts.append(counts)
            all_preds.append(pred_count)

    # Calculate metrics
    mae = np.mean(all_mae)
    mse = np.sqrt(np.mean(all_mse))  # RMSE

    print(f"\n📊 Test Set Results:")
    print(f"   MAE: {mae:.2f}")
    print(f"   RMSE: {mse:.2f}")
    print(f"   Min Error: {min(all_mae):.2f}")
    print(f"   Max Error: {max(all_mae):.2f}")
    print(f"   Median Error: {np.median(all_mae):.2f}")

    # Show worst predictions
    worst_indices = np.argsort(all_mae)[-5:]
    print(f"\n⚠️  Worst 5 Predictions:")
    for idx in reversed(worst_indices):
        print(f"   GT: {all_counts[idx]:.0f}, Pred: {all_preds[idx]:.1f}, Error: {all_mae[idx]:.1f}")

    # Show best predictions
    best_indices = np.argsort(all_mae)[:5]
    print(f"\n✅ Best 5 Predictions:")
    for idx in best_indices:
        print(f"   GT: {all_counts[idx]:.0f}, Pred: {all_preds[idx]:.1f}, Error: {all_mae[idx]:.1f}")

    return mae, mse


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', required=True,
                       help='Path to checkpoint')
    parser.add_argument('--data-root', required=True,
                       help='Path to ShanghaiTech part_A or part_B')
    parser.add_argument('--device', default='cuda')

    args = parser.parse_args()

    evaluate_testset(args.checkpoint, args.data_root, args.device)
```

### Run evaluation:

```bash
python evaluate_testset.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --data-root datasets/ShanghaiTech/part_A
```

---

## 🎨 Visualize Multiple Results

### visualize_results.py

```python
import matplotlib.pyplot as plt
import glob
import os
from test_finetuned import load_finetuned_model, predict_count

def visualize_grid(checkpoint_path, image_dir, num_images=9, device='cuda'):
    """Show grid of predictions"""

    model = load_finetuned_model(checkpoint_path, device)
    image_paths = glob.glob(os.path.join(image_dir, '*.jpg'))[:num_images]

    rows = int(np.sqrt(num_images))
    cols = (num_images + rows - 1) // rows

    fig, axes = plt.subplots(rows, cols, figsize=(20, 20))
    axes = axes.flatten()

    for idx, img_path in enumerate(image_paths):
        count, density = predict_count(model, img_path, device, visualize=False)

        # Load image
        img = plt.imread(img_path)

        # Plot
        axes[idx].imshow(img)
        axes[idx].imshow(density[0, 0].cpu().numpy(), cmap='jet', alpha=0.5)
        axes[idx].set_title(f'{os.path.basename(img_path)}\nCount: {count:.1f}')
        axes[idx].axis('off')

    plt.tight_layout()
    plt.savefig('predictions_grid.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✅ Saved: predictions_grid.png")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--images', required=True)
    parser.add_argument('--num', type=int, default=9)

    args = parser.parse_args()

    visualize_grid(args.checkpoint, args.images, args.num)
```

### Run it:

```bash
python visualize_results.py \
    --checkpoint checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth \
    --images datasets/ShanghaiTech/part_A/test_data/images/ \
    --num 16
```

---

## 🚀 Deploy Fine-tuned Model

Update your FastAPI to use the fine-tuned model:

### models/vmamba/api.py

```python
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import torch
from torchvision import transforms
import io
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from models.vmamba_tmtb import VMambaTMTB

app = FastAPI(title="VMamba Crowd Counter")

# Load fine-tuned model
CHECKPOINT_PATH = "checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth"
device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = VMambaTMTB()
checkpoint = torch.load(CHECKPOINT_PATH, map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])
model.to(device)
model.eval()

print(f"✅ Loaded fine-tuned VMamba model")

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225])
])


@app.post("/count")
async def count_people(file: UploadFile = File(...)):
    """Count people in uploaded image"""

    # Read image
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert('RGB')

    # Preprocess
    img_tensor = transform(img).unsqueeze(0).to(device)

    # Predict
    with torch.no_grad():
        density_map = model(img_tensor)

    count = density_map.sum().item()

    return {
        "count": round(count, 1),
        "model": "VMamba-TMTB (fine-tuned on ShanghaiTech)"
    }


@app.get("/")
def root():
    return {"message": "VMamba Crowd Counter API"}
```

### Run it:

```bash
uvicorn models.vmamba.api:app --reload --port 8000
```

---

## 📈 Expected Results

### ShanghaiTech Part A (Dense Crowds)

- **Good**: MAE 60-80
- **Excellent**: MAE < 60
- **State-of-the-art**: MAE 50-55

### ShanghaiTech Part B (Sparse Crowds)

- **Good**: MAE 8-12
- **Excellent**: MAE < 8
- **State-of-the-art**: MAE 6-7

---

## 🔥 Next Steps

1. ✅ Train model (`finetune_vmamba.py`)
2. ✅ Test on single image (`test_finetuned.py`)
3. ✅ Evaluate on test set (`evaluate_testset.py`)
4. ✅ Deploy with FastAPI (`models/vmamba/api.py`)
5. ✅ Connect to your React frontend

Good luck! 🎯
