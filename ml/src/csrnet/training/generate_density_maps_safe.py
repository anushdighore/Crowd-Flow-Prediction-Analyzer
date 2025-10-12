"""
Safe CSRNet Density Map Generator
Optimized for stability on i5 13th Gen HX + RTX 3050
Prevents VS Code crashes with controlled resource usage
"""
import numpy as np
import h5py
import scipy.io as io
import scipy.spatial
import scipy.ndimage
from PIL import Image
import os
from pathlib import Path
from tqdm import tqdm
import multiprocessing as mp
from functools import partial
import time
import gc


# =====================================================
# SAFE CONFIGURATION FOR YOUR SYSTEM
# =====================================================
def get_safe_worker_count():
    """
    Optimized worker calculation for i5 13th Gen HX
    20 logical cores total - use 80% for maximum performance
    """
    total = mp.cpu_count()
    
    # For 20-core systems: use 16 workers (80% utilization)
    # Leaves 4 cores for VS Code and OS - good balance
    if total >= 16:
        return 16
    elif total >= 8:
        return 6
    elif total >= 4:
        return 3
    else:
        return 1


SAFE_NUM_WORKERS = get_safe_worker_count()


def gaussian_filter_density(gt):
    """Generate density map using Gaussian filter with adaptive kernel"""
    density = np.zeros(gt.shape, dtype=np.float32)
    gt_count = np.count_nonzero(gt)

    if gt_count == 0:
        return density

    pts = np.array(list(zip(np.nonzero(gt)[1], np.nonzero(gt)[0])))

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

        density += scipy.ndimage.gaussian_filter(pt2d, sigma, mode='constant')

    return density


def generate_density_map_from_mat(mat_path, img_shape):
    """Generate density map from .mat annotation file"""
    try:
        mat = io.loadmat(mat_path)

        if 'image_info' in mat:
            points = mat['image_info'][0, 0][0, 0][0]
        elif 'annPoints' in mat:
            points = mat['annPoints']
        else:
            raise KeyError(f"Cannot find annotation key in {mat_path}")

        h, w = img_shape
        gt = np.zeros((h, w), dtype=np.float32)

        for point in points:
            x, y = int(point[0]), int(point[1])
            if 0 <= x < w and 0 <= y < h:
                gt[y, x] = 1

        density_map = gaussian_filter_density(gt)
        return density_map, density_map.sum()
        
    except Exception as e:
        raise Exception(f"Error processing {mat_path}: {str(e)}")


def process_single_image(args):
    """
    Process a single image - designed for safe multiprocessing
    Returns: (success: bool, img_name: str, people_count: float, error_msg: str)
    """
    img_path, gt_dir, output_dir = args
    
    try:
        # Load image
        with Image.open(img_path) as img:
            img_shape = (img.size[1], img.size[0])  # (height, width)

        # Find .mat file
        img_name = img_path.stem
        mat_path = gt_dir / f"GT_{img_name}.mat"

        if not mat_path.exists():
            return (False, img_name, 0, f"Mat file not found: {mat_path.name}")

        # Generate density map
        density_map, people_count = generate_density_map_from_mat(str(mat_path), img_shape)

        # Save as .h5
        output_path = output_dir / f"{img_name}.h5"
        with h5py.File(str(output_path), 'w') as hf:
            hf['density'] = density_map

        # Force garbage collection to prevent memory buildup
        del density_map
        
        return (True, img_name, people_count, None)

    except Exception as e:
        return (False, img_path.stem if hasattr(img_path, 'stem') else 'unknown', 0, str(e))


def process_dataset_safe(part_a_root, output_root, num_workers):
    """Process dataset using safe multiprocessing"""

    print("="*70)
    print("� HIGH-PERFORMANCE CSRNet Density Map Generator")
    print(f"   Optimized for: i5 13th Gen HX + RTX 3050")
    print(f"   Workers: {num_workers} (high-performance mode)")
    print("="*70)

    stats = {}

    for split in ['train_data', 'test_data']:
        split_name = "train" if "train" in split else "test"

        print(f"\n{'='*70}")
        print(f"📁 Processing {split_name.upper()} SET")
        print('='*70)

        start_time = time.time()

        # Setup paths
        img_dir = part_a_root / split / "images"
        gt_dir = part_a_root / split / "ground-truth"

        if not gt_dir.exists():
            gt_dir = part_a_root / split / "ground_truth"

        if not img_dir.exists() or not gt_dir.exists():
            print(f"⚠️  Skipping {split_name}: directories not found")
            continue

        # Create output directory
        output_dir = Path(output_root) / "part_A" / split / "density_maps"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get all images
        img_files = sorted(img_dir.glob("*.jpg"))
        print(f"\n📊 Found {len(img_files)} images")
        print(f"⚡ Processing with {num_workers} safe parallel workers...")
        print(f"💡 This prevents system overload and VS Code crashes\n")

        # Prepare arguments for parallel processing
        process_args = [(img_path, gt_dir, output_dir) for img_path in img_files]

        # Process in parallel with controlled resources
        success_count = 0
        total_people = 0
        errors = []

        # Use spawn context for better stability on Windows
        ctx = mp.get_context('spawn')
        
        with ctx.Pool(processes=num_workers) as pool:
            # Use smaller chunksize for better progress reporting and less memory pressure
            results = list(tqdm(
                pool.imap(process_single_image, process_args, chunksize=1),
                total=len(img_files),
                desc=f"   Generating {split_name} density maps",
                unit="img"
            ))

        # Aggregate results
        for (success, img_name, people_count, error_msg) in results:
            if success:
                success_count += 1
                total_people += people_count
            else:
                errors.append(f"{img_name}: {error_msg}")

        elapsed_time = time.time() - start_time

        # Store statistics
        stats[split_name] = {
            "total": len(img_files),
            "success": success_count,
            "people": int(total_people),
            "avg_count": total_people / success_count if success_count > 0 else 0,
            "time": elapsed_time,
            "speed": len(img_files) / elapsed_time if elapsed_time > 0 else 0
        }

        print(f"\n✅ Generated: {success_count}/{len(img_files)} density maps")
        print(f"👥 Total people: {int(total_people)}")
        print(f"📈 Average per image: {total_people/success_count:.1f}")
        print(f"⏱️  Time: {elapsed_time:.1f}s ({stats[split_name]['speed']:.2f} images/sec)")
        print(f"📂 Saved to: {output_dir}")

        if errors:
            print(f"\n⚠️  {len(errors)} errors occurred:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more")

        # Force garbage collection between splits
        gc.collect()

    return stats


def verify_and_summarize(output_root, stats):
    """Verification and final summary"""

    print("\n" + "="*70)
    print("🔍 VERIFICATION REPORT")
    print("="*70)

    for split in ['train_data', 'test_data']:
        split_name = "TRAIN" if "train" in split else "TEST"
        density_dir = Path(output_root) / "part_A" / split / "density_maps"

        if not density_dir.exists():
            continue

        density_files = list(density_dir.glob("*.h5"))
        print(f"\n{split_name} SET: {len(density_files)} files")

        if density_files:
            # Sample first file
            with h5py.File(str(density_files[0]), 'r') as f:
                density = f['density'][:]
                print(f"  Sample: {density_files[0].name}")
                print(f"  Shape: {density.shape}")
                print(f"  Count: {density.sum():.2f} people")

    # Final summary
    print("\n" + "="*70)
    print("✅ GENERATION COMPLETE - PERFORMANCE SUMMARY")
    print("="*70)

    total_time = 0
    total_images = 0

    for split_name in ['train', 'test']:
        if split_name in stats:
            s = stats[split_name]
            print(f"\n{split_name.upper()} SET:")
            print(f"  Images: {s['success']}/{s['total']}")
            print(f"  People: {s['people']}")
            print(f"  Time: {s['time']:.1f}s")
            print(f"  Speed: {s['speed']:.2f} images/sec")
            total_time += s['time']
            total_images += s['success']

    if total_images > 0:
        print(f"\n📊 OVERALL:")
        print(f"  Total images: {total_images}")
        print(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"  Average speed: {total_images/total_time:.2f} images/sec")
        print(f"\n💡 Safe mode ensures stability - no crashes!")


# =====================================================
# MAIN EXECUTION
# =====================================================
if __name__ == "__main__":
    import argparse

    # Required for Windows multiprocessing
    mp.freeze_support()

    parser = argparse.ArgumentParser(
        description='Safe CSRNet Density Map Generator (prevents crashes)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (recommended)
  python generate_density_maps_safe.py

  # Specify custom paths
  python generate_density_maps_safe.py --dataset-root <path> --output-root <path>

  # Use more workers (if system is stable)
  python generate_density_maps_safe.py --workers 8
        """
    )
    
    parser.add_argument('--dataset-root', type=str,
                       default='D:\\College\\Major Project\\ml\\datasets\\raw\\ShanghaiTech\\ShanghaiTech',
                       help='Root directory of ShanghaiTech dataset')
    parser.add_argument('--output-root', type=str,
                       default='D:\\College\\Major Project\\ml\\datasets\\processed\\shanghaiTech',
                       help='Output directory for density maps')
    parser.add_argument('--workers', type=int,
                       default=SAFE_NUM_WORKERS,
                       help=f'Number of parallel workers (default: {SAFE_NUM_WORKERS}, max recommended: 16)')

    args = parser.parse_args()
    
    # Clamp workers to safe range
    num_workers = max(1, min(args.workers, 16))
    
    if args.workers != num_workers:
        print(f"⚠️  Clamped workers from {args.workers} to {num_workers} for safety\n")

    # Find dataset
    dataset_root = Path(args.dataset_root)
    if not dataset_root.exists():
        print(f"❌ Dataset not found: {dataset_root}")
        print(f"   Please check the path and try again")
        exit(1)

    # Find part_A
    part_a_root = dataset_root / "part_A"
    if not part_a_root.exists():
        print(f"❌ Part A not found: {part_a_root}")
        print(f"   Expected structure: {dataset_root}/part_A/")
        exit(1)

    print(f"🔧 System: i5 13th Gen HX ({mp.cpu_count()} cores)")
    print(f"🔧 Workers: {num_workers} (safe mode)")
    print(f"📂 Dataset: {part_a_root}")
    print(f"📂 Output: {args.output_root}\n")

    # Process dataset
    try:
        stats = process_dataset_safe(part_a_root, args.output_root, num_workers)

        # Verify and summarize
        verify_and_summarize(args.output_root, stats)

        print("\n" + "="*70)
        print("🎉 All Done! No crashes!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Partial results may be saved")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
