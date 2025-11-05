# ShanghaiTech Dataset Preparation Guide

## 📥 Download the Dataset

### Option 1: Official Google Drive (Recommended)

```
https://drive.google.com/drive/folders/1CrdJkgDdwNw4g5D7D-q7wJxJpDlsWfM9
```

### Option 2: Kaggle

```bash
# Install Kaggle CLI
pip install kaggle

# Download ShanghaiTech Part A
kaggle datasets download -d tthien/shanghaitech

# Extract
unzip shanghaitech.zip -d datasets/
```

### Option 3: GitHub Mirror

```bash
git clone https://github.com/desenzhou/ShanghaiTechDataset.git datasets/ShanghaiTech
```

---

## 📁 Expected Directory Structure

After downloading, organize like this:

```
datasets/
└── ShanghaiTech/
    ├── part_A/
    │   ├── train_data/
    │   │   ├── images/
    │   │   │   ├── IMG_1.jpg
    │   │   │   ├── IMG_2.jpg
    │   │   │   └── ...
    │   │   └── ground-truth/
    │   │       ├── IMG_1.h5
    │   │       ├── IMG_2.h5
    │   │       └── ...
    │   └── test_data/
    │       ├── images/
    │       │   └── ...
    │       └── ground-truth/
    │           └── ...
    └── part_B/
        ├── train_data/
        └── test_data/
```

---

## 🔧 Generate Ground Truth Density Maps

If your dataset only has annotation points (.mat files), run this script:

### create_density_maps.py

```python
import numpy as np
import h5py
import scipy.io as io
import scipy.spatial
from scipy.ndimage import gaussian_filter
from PIL import Image
import os
from tqdm import tqdm


def generate_density_map(annotation_points, image_shape):
    """
    Generate Gaussian density map from annotation points

    Args:
        annotation_points: Nx2 array of (x, y) coordinates
        image_shape: (height, width) of image

    Returns:
        density_map: HxW density map
    """
    h, w = image_shape
    density_map = np.zeros((h, w), dtype=np.float32)

    num_points = len(annotation_points)
    if num_points == 0:
        return density_map

    # For each annotation point
    for i, point in enumerate(annotation_points):
        x, y = int(point[0]), int(point[1])

        # Skip if out of bounds
        if x >= w or y >= h or x < 0 or y < 0:
            continue

        # Calculate adaptive gaussian kernel size
        # Based on k-nearest neighbors (k=3)
        if num_points > 1:
            tree = scipy.spatial.KDTree(annotation_points.copy(), leafsize=2048)
            distances, _ = tree.query(point, k=4)  # k=4 to exclude self
            sigma = np.mean(distances[1:4]) * 0.3  # Adaptive sigma
        else:
            sigma = 15  # Default sigma for single person

        # Create Gaussian kernel
        kernel_size = int(sigma * 3)
        x_range = range(max(0, x - kernel_size), min(w, x + kernel_size + 1))
        y_range = range(max(0, y - kernel_size), min(h, y + kernel_size + 1))

        for xi in x_range:
            for yi in y_range:
                dist = (xi - x) ** 2 + (yi - y) ** 2
                density_map[yi, xi] += np.exp(-dist / (2 * sigma ** 2))

    return density_map


def process_dataset(root_dir, part='A'):
    """Process ShanghaiTech dataset to generate density maps"""

    part_dir = os.path.join(root_dir, f'part_{part}')

    for split in ['train_data', 'test_data']:
        img_dir = os.path.join(part_dir, split, 'images')
        gt_dir = os.path.join(part_dir, split, 'ground-truth')
        mat_dir = os.path.join(part_dir, split, 'ground_truth')  # Original annotations

        os.makedirs(gt_dir, exist_ok=True)

        # Get all images
        img_files = sorted([f for f in os.listdir(img_dir) if f.endswith('.jpg')])

        print(f"\nProcessing {part}_{split}...")
        for img_file in tqdm(img_files):
            # Load image to get shape
            img_path = os.path.join(img_dir, img_file)
            img = Image.open(img_path)
            w, h = img.size

            # Load annotation
            mat_file = img_file.replace('.jpg', '.mat')
            mat_path = os.path.join(mat_dir, f'GT_{mat_file}')

            mat = io.loadmat(mat_path)
            points = mat['image_info'][0,0][0,0][0]  # Extract annotation points

            # Generate density map
            density = generate_density_map(points, (h, w))

            # Save as HDF5
            h5_path = os.path.join(gt_dir, img_file.replace('.jpg', '.h5'))
            with h5py.File(h5_path, 'w') as f:
                f['density'] = density
                f['count'] = len(points)

        print(f"✅ Processed {len(img_files)} files")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='datasets/ShanghaiTech',
                       help='Root directory of ShanghaiTech dataset')
    parser.add_argument('--part', default='A', choices=['A', 'B'],
                       help='Dataset part (A or B)')

    args = parser.parse_args()

    process_dataset(args.root, args.part)
    print("\n🎉 Done! Density maps saved as .h5 files")
```

### Run it:

```bash
# For Part A
python create_density_maps.py --root datasets/ShanghaiTech --part A

# For Part B
python create_density_maps.py --root datasets/ShanghaiTech --part B
```

---

## 📊 Dataset Statistics

### Part A (Dense crowds)

- **Train**: 300 images
- **Test**: 182 images
- **Average crowd**: 501 people per image
- **Total annotations**: 241,677 people
- **Characteristics**: Large gatherings, concerts, protests

### Part B (Sparse crowds)

- **Train**: 400 images
- **Test**: 316 images
- **Average crowd**: 123 people per image
- **Total annotations**: 88,488 people
- **Characteristics**: Streets, malls, queues

---

## ✅ Verify Dataset

Run this verification script:

```python
import os
import h5py
from PIL import Image

def verify_dataset(root_dir, part='A'):
    part_dir = os.path.join(root_dir, f'part_{part}')

    for split in ['train_data', 'test_data']:
        img_dir = os.path.join(part_dir, split, 'images')
        gt_dir = os.path.join(part_dir, split, 'ground-truth')

        img_files = set([f.replace('.jpg', '') for f in os.listdir(img_dir) if f.endswith('.jpg')])
        gt_files = set([f.replace('.h5', '') for f in os.listdir(gt_dir) if f.endswith('.h5')])

        missing_gt = img_files - gt_files
        extra_gt = gt_files - img_files

        print(f"\n{part}_{split}:")
        print(f"  Images: {len(img_files)}")
        print(f"  Ground truth: {len(gt_files)}")

        if missing_gt:
            print(f"  ⚠️  Missing GT: {missing_gt}")
        if extra_gt:
            print(f"  ⚠️  Extra GT: {extra_gt}")

        if not missing_gt and not extra_gt:
            print(f"  ✅ All files matched!")

verify_dataset('datasets/ShanghaiTech', 'A')
```

---

## 🚀 Start Fine-tuning

Once dataset is ready:

```bash
# Fine-tune on Part A (dense crowds)
python finetune_vmamba.py \
    --checkpoint checkpoints/jhu_5.pth \
    --data-root datasets/ShanghaiTech/part_A \
    --epochs 50 \
    --batch-size 8 \
    --lr 1e-5

# Fine-tune on Part B (sparse crowds)
python finetune_vmamba.py \
    --checkpoint checkpoints/jhu_5.pth \
    --data-root datasets/ShanghaiTech/part_B \
    --epochs 50 \
    --batch-size 8 \
    --lr 1e-5
```

---

## 💡 Tips

1. **Start with Part B** if you have limited GPU memory (smaller crowds = lower memory usage)

2. **Part A is harder** but gives better results on dense crowds

3. **Expected training time**:

   - Part A: 4-6 hours (GTX 1080 Ti)
   - Part B: 3-5 hours (GTX 1080 Ti)

4. **Expected MAE** (Mean Absolute Error):

   - Part A: 60-80 (good), <60 (excellent)
   - Part B: 8-12 (good), <8 (excellent)

5. **If out of memory**: Reduce `--batch-size` to 4 or 2

6. **Resume training**: Modify `finetune_vmamba.py` to load from checkpoint:
   ```python
   checkpoint = torch.load('checkpoints/vmamba_finetuned/vmamba_shanghai_epoch10.pth')
   model.load_state_dict(checkpoint['model_state_dict'])
   optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
   start_epoch = checkpoint['epoch'] + 1
   ```

---

## 📝 Next Steps

After training completes:

1. **Best model**: `checkpoints/vmamba_finetuned/vmamba_shanghai_best.pth`
2. **Test it**: See `TEST_FINETUNED_MODEL.md`
3. **Deploy**: Update FastAPI to use fine-tuned model
4. **Compare**: Test against CSRNet baseline

Good luck! 🎯
