"""
PyTorch Dataset for CSRNet Training on ShanghaiTech Part A
"""
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms
from PIL import Image
import h5py
import numpy as np
from pathlib import Path
import random
import math


def _next_multiple(x: int, m: int = 8) -> int:
    """Return the next multiple of m greater than or equal to x."""
    return int(math.ceil(x / m) * m)


def collate_csrnet_pad(batch, multiple: int = 8):
    """
    Collate function that pads variable-size images/density maps in a batch.
    IMPORTANT: Density maps are expected to be 8x downsampled relative to images.

    Args:
        batch: list of tuples (img: Tensor[C,H,W], density: Tensor[1,H//8,W//8], count: float)
        multiple: ensure padded image H,W are divisible by this (CSRNet downsamples by 8)

    Returns:
        imgs: Tensor[N,C,H_pad,W_pad]
        densities: Tensor[N,1,H_pad//8,W_pad//8]
        counts: Tensor[N]
    """
    imgs, densities, counts = zip(*batch)

    # Get max height/width in this batch for IMAGES
    max_h = max(t.shape[1] for t in imgs)
    max_w = max(t.shape[2] for t in imgs)

    # Round up to next multiple for safe downsampling
    pad_h = _next_multiple(max_h, multiple)
    pad_w = _next_multiple(max_w, multiple)
    
    # Density maps are 8x downsampled
    density_pad_h = pad_h // 8
    density_pad_w = pad_w // 8

    n = len(imgs)
    c = imgs[0].shape[0]

    padded_imgs = torch.zeros((n, c, pad_h, pad_w), dtype=imgs[0].dtype)
    padded_dens = torch.zeros((n, 1, density_pad_h, density_pad_w), dtype=densities[0].dtype)

    for i, (im, dm) in enumerate(zip(imgs, densities)):
        h, w = im.shape[1], im.shape[2]
        padded_imgs[i, :, :h, :w] = im
        # Density is already downsampled, so use its actual size
        padded_dens[i, :, :dm.shape[1], :dm.shape[2]] = dm

    counts_tensor = torch.tensor(counts, dtype=torch.float32)
    return padded_imgs, padded_dens, counts_tensor


class ShanghaiTechDataset(Dataset):
    """
    ShanghaiTech Dataset for CSRNet Training
    
    Loads images and corresponding density maps for training/testing
    """
    
    def __init__(self, 
                 img_root,
                 density_root,
                 split='train',
                 transform=None,
                 augment=False):
        """
        Args:
            img_root: Path to images directory (e.g., ml/datasets/raw/ShanghaiTech/ShanghaiTech/part_A/train_data/images)
            density_root: Path to density maps directory (e.g., ml/datasets/processed/part_A/train_data/density_maps)
            split: 'train' or 'test'
            transform: Image transformation (default: ToTensor + Normalize)
            augment: Apply data augmentation (only for training)
        """
        self.img_root = Path(img_root)
        self.density_root = Path(density_root)
        self.split = split
        self.augment = augment
        
        # Get all image files
        self.img_files = sorted(self.img_root.glob("*.jpg"))
        
        if len(self.img_files) == 0:
            raise ValueError(f"No images found in {self.img_root}")
        
        print(f"📁 Loaded {len(self.img_files)} images from {split} set")
        
        # Default transform: ToTensor + ImageNet Normalization
        if transform is None:
            self.transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
        else:
            self.transform = transform
        
        # Augmentation transforms (only for training)
        if self.augment:
            self.aug_transform = transforms.Compose([
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.RandomHorizontalFlip(p=0.5),
            ])
        else:
            self.aug_transform = None
    
    def __len__(self):
        return len(self.img_files)
    
    def __getitem__(self, idx):
        """
        Returns:
            img: Transformed image tensor (C, H, W)
            density: Density map tensor (1, H, W)
            count: Ground truth count (scalar)
        """
        # Load image
        img_path = self.img_files[idx]
        img = Image.open(img_path).convert('RGB')
        
        # Load density map
        img_name = img_path.stem
        density_path = self.density_root / f"{img_name}.h5"
        
        if not density_path.exists():
            raise FileNotFoundError(f"Density map not found: {density_path}")
        
        with h5py.File(str(density_path), 'r') as hf:
            density = hf['density'][:]
        
        # Ground truth count
        count = density.sum()
        
        # Apply augmentation (for training only)
        if self.augment and self.aug_transform is not None:
            # Apply color jitter and flip
            img = self.aug_transform(img)
            
            # If flipped, flip density map too
            if random.random() > 0.5:
                density = np.fliplr(density).copy()
        
        # Apply transform to image
        img = self.transform(img)
        
        # Convert density map to tensor and downsample to match CSRNet output
        # CSRNet has 3 MaxPool layers (2x2), so output is 8x downsampled
        density = torch.from_numpy(density).unsqueeze(0)  # (1, H, W)
        
        # Downsample density map by 8x using average pooling
        # This ensures the sum (total count) is preserved
        downsample_factor = 8
        if density.shape[1] % downsample_factor != 0 or density.shape[2] % downsample_factor != 0:
            # Pad to make divisible by 8
            pad_h = (downsample_factor - density.shape[1] % downsample_factor) % downsample_factor
            pad_w = (downsample_factor - density.shape[2] % downsample_factor) % downsample_factor
            density = torch.nn.functional.pad(density, (0, pad_w, 0, pad_h), mode='constant', value=0)
        
        # Downsample using average pooling to preserve count
        density = torch.nn.functional.avg_pool2d(density.unsqueeze(0), 
                                                  kernel_size=downsample_factor, 
                                                  stride=downsample_factor).squeeze(0)
        
        # Scale by factor^2 to preserve the sum (count)
        density = density * (downsample_factor ** 2)
        
        return img, density, count


class ShanghaiTechPartA:
    """
    Convenience class for loading ShanghaiTech Part A train/test datasets
    """
    
    def __init__(self,
                 dataset_root='ml/datasets/raw/ShanghaiTech/ShanghaiTech',
                 density_root='ml/datasets/processed',
                 batch_size=4,
                 num_workers=2,
                 augment_train=True):
        """
        Args:
            dataset_root: Root directory of ShanghaiTech dataset
            density_root: Root directory of density maps
            batch_size: Batch size for DataLoader
            num_workers: Number of workers for DataLoader
            augment_train: Apply augmentation to training set
        """
        self.dataset_root = Path(dataset_root)
        self.density_root = Path(density_root)
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.augment_train = augment_train
        
        # Paths
        self.train_img_dir = self.dataset_root / "part_A" / "train_data" / "images"
        self.test_img_dir = self.dataset_root / "part_A" / "test_data" / "images"
        self.train_density_dir = self.density_root / "part_A" / "train_data" / "density_maps"
        self.test_density_dir = self.density_root / "part_A" / "test_data" / "density_maps"
    
    def get_train_loader(self):
        """Get training DataLoader with optimized settings"""
        train_dataset = ShanghaiTechDataset(
            img_root=self.train_img_dir,
            density_root=self.train_density_dir,
            split='train',
            augment=self.augment_train
        )
        
        # Determine optimal num_workers
        # Use user-specified if provided, otherwise use 6 (optimal for i5 13th gen)
        num_workers = self.num_workers if self.num_workers is not None else 6
        
        train_loader = torch.utils.data.DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True,
            persistent_workers=True if num_workers > 0 else False,
            prefetch_factor=2 if num_workers > 0 else None,
            collate_fn=collate_csrnet_pad
        )
        
        return train_loader
    
    def get_test_loader(self):
        """Get test DataLoader with optimized settings"""
        test_dataset = ShanghaiTechDataset(
            img_root=self.test_img_dir,
            density_root=self.test_density_dir,
            split='test',
            augment=False  # No augmentation for test
        )
        
        # Use fewer workers for validation (4 is sufficient)
        num_workers = min(self.num_workers, 4) if self.num_workers is not None else 4
        
        test_loader = torch.utils.data.DataLoader(
            test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
            persistent_workers=True if num_workers > 0 else False,
            prefetch_factor=2 if num_workers > 0 else None,
            collate_fn=collate_csrnet_pad
        )
        
        return test_loader


if __name__ == "__main__":
    # Test dataset loading
    print("🧪 Testing dataset loading...")
    
    # Create dataset with absolute paths
    data = ShanghaiTechPartA(
        dataset_root='D:\\College\\Major Project\\ml\\datasets\\raw\\ShanghaiTech\\ShanghaiTech',
        density_root='D:\\College\\Major Project\\ml\\datasets\\processed\\shanghaiTech',
        batch_size=2
    )
    
    # Get loaders
    train_loader = data.get_train_loader()
    test_loader = data.get_test_loader()
    
    print(f"\n📊 Dataset Stats:")
    print(f"   Train batches: {len(train_loader)}")
    print(f"   Test batches: {len(test_loader)}")
    
    # Test loading one batch
    print(f"\n🔍 Testing batch loading...")
    img, density, count = next(iter(train_loader))
    
    print(f"   Image shape: {img.shape}")
    print(f"   Density shape: {density.shape}")
    print(f"   Counts: {count.tolist()}")
    print(f"   Image range: [{img.min():.3f}, {img.max():.3f}]")
    print(f"   Density range: [{density.min():.3f}, {density.max():.3f}]")
    
    print("\n✅ Dataset test complete!")
