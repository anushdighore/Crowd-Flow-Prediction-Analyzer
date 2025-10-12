"""
Generate Density Maps for CSRNet Training
Processes ShanghaiTech Part A dataset
"""
import numpy as np
import h5py
import scipy.io as io
import scipy.spatial
from PIL import Image
import os
from pathlib import Path
from tqdm import tqdm
import argparse


def gaussian_filter_density(gt):
    """
    Generate density map using Gaussian filter
    Uses adaptive kernel based on k-nearest neighbors
    
    Args:
        gt: Ground truth points array (N, 2) with (x, y) coordinates
        
    Returns:
        density: Density map (H, W)
    """
    density = np.zeros(gt.shape, dtype=np.float32)
    gt_count = np.count_nonzero(gt)
    
    if gt_count == 0:
        return density
    
    # Get non-zero point locations
    pts = np.array(list(zip(np.nonzero(gt)[1], np.nonzero(gt)[0])))
    
    # Adaptive gaussian kernel
    leafsize = 2048
    tree = scipy.spatial.KDTree(pts.copy(), leafsize=leafsize)
    
    distances, locations = tree.query(pts, k=4)
    
    for i, pt in enumerate(pts):
        pt2d = np.zeros(gt.shape, dtype=np.float32)
        pt2d[pt[1], pt[0]] = 1.0
        
        if gt_count > 1:
            sigma = (distances[i][1] + distances[i][2] + distances[i][3]) * 0.1
        else:
            sigma = np.average(np.array(gt.shape)) / 2.0 / 2.0
        
        # Apply gaussian filter
        density += scipy.ndimage.gaussian_filter(pt2d, sigma, mode='constant')
    
    return density


def generate_density_map_from_mat(mat_path, img_shape):
    """
    Generate density map from .mat annotation file
    
    Args:
        mat_path: Path to .mat file
        img_shape: (height, width) of image
        
    Returns:
        density_map: Generated density map
    """
    # Load .mat file
    mat = io.loadmat(mat_path)
    
    # Get annotation points - try different possible keys
    if 'image_info' in mat:
        points = mat['image_info'][0, 0][0, 0][0]
    elif 'annPoints' in mat:
        points = mat['annPoints']
    else:
        raise KeyError(f"Cannot find annotation key in {mat_path}")
    
    # Create point map
    h, w = img_shape
    gt = np.zeros((h, w), dtype=np.float32)
    
    for point in points:
        x, y = int(point[0]), int(point[1])
        if 0 <= x < w and 0 <= y < h:
            gt[y, x] = 1
    
    # Generate density map
    density_map = gaussian_filter_density(gt)
    
    return density_map


def process_shanghaitech_part_a(dataset_root, output_root):
    """
    Process ShanghaiTech Part A dataset
    
    Args:
        dataset_root: Root directory of ShanghaiTech dataset
        output_root: Output directory for density maps
    """
    print("🎯 Processing ShanghaiTech Part A")
    print(f"   Dataset: {dataset_root}")
    print(f"   Output: {output_root}")
    
    part_a_dir = Path(dataset_root) / "part_A"
    
    if not part_a_dir.exists():
        raise FileNotFoundError(f"Part A directory not found: {part_a_dir}")
    
    # Process train and test
    for split in ['train_data', 'test_data']:
        print(f"\n📁 Processing {split}...")
        
        img_dir = part_a_dir / split / "images"
        gt_dir = part_a_dir / split / "ground-truth"
        
        if not img_dir.exists():
            print(f"   ⚠️  Images not found: {img_dir}")
            continue
        
        if not gt_dir.exists():
            # Try alternate name
            gt_dir = part_a_dir / split / "ground_truth"
            if not gt_dir.exists():
                print(f"   ⚠️  Ground truth not found")
                continue
        
        # Create output directory
        output_dir = Path(output_root) / "part_A" / split / "density_maps"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all images
        img_files = sorted(img_dir.glob("*.jpg"))
        print(f"   Found {len(img_files)} images")
        
        # Process each image
        success_count = 0
        for img_path in tqdm(img_files, desc=f"   Generating density maps"):
            try:
                # Load image to get shape
                img = Image.open(img_path)
                img_shape = (img.size[1], img.size[0])  # (height, width)
                
                # Find corresponding .mat file
                img_name = img_path.stem
                mat_path = gt_dir / f"GT_{img_name}.mat"
                
                if not mat_path.exists():
                    print(f"   ⚠️  Annotation not found: {mat_path.name}")
                    continue
                
                # Generate density map
                density_map = generate_density_map_from_mat(str(mat_path), img_shape)
                
                # Save as .h5 file
                output_path = output_dir / f"{img_name}.h5"
                with h5py.File(str(output_path), 'w') as hf:
                    hf['density'] = density_map
                
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Error processing {img_path.name}: {e}")
                continue
        
        print(f"   ✅ Successfully generated {success_count}/{len(img_files)} density maps")
        print(f"   📂 Saved to: {output_dir}")


def verify_density_maps(output_root):
    """Verify generated density maps"""
    print("\n🔍 Verifying density maps...")
    
    part_a_dir = Path(output_root) / "part_A"
    
    for split in ['train_data', 'test_data']:
        density_dir = part_a_dir / split / "density_maps"
        
        if not density_dir.exists():
            print(f"   ⚠️  {split} density maps not found")
            continue
        
        density_files = list(density_dir.glob("*.h5"))
        print(f"\n   {split}: {len(density_files)} density maps")
        
        if len(density_files) > 0:
            # Load first file to check
            sample = h5py.File(str(density_files[0]), 'r')
            density = sample['density'][:]
            print(f"   Sample shape: {density.shape}")
            print(f"   Sample count: {density.sum():.2f}")
            print(f"   Sample range: [{density.min():.4f}, {density.max():.4f}]")
            sample.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate density maps for ShanghaiTech Part A')
    parser.add_argument('--dataset-root', type=str, 
                       default='ml/datasets/raw/ShanghaiTech/ShanghaiTech',
                       help='Root directory of ShanghaiTech dataset')
    parser.add_argument('--output-root', type=str,
                       default='ml/datasets/processed',
                       help='Output directory for density maps')
    
    args = parser.parse_args()
    
    # Process dataset
    process_shanghaitech_part_a(args.dataset_root, args.output_root)
    
    # Verify
    verify_density_maps(args.output_root)
    
    print("\n✅ Density map generation complete!")
