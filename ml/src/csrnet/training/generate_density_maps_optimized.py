"""
OPTIMIZED CSRNet Density Map Generator
Uses multiprocessing for significant speedup on multi-core CPUs
Best for: Local machines with 4+ cores
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


# =====================================================
# CONFIGURATION
# =====================================================
# Adjust based on your CPU cores
# i5 13th Gen HX has 20 threads, but using every logical core adds heavy overhead
# Determine a safe default that leaves headroom for IDE / OS stability
def _determine_default_workers():
    total = mp.cpu_count()

    # Leave at least 4 logical cores idle and cap aggressive usage
    if total >= 16:
        return min(8, total - 4)
    if total >= 8:
        return max(4, total // 2)
    return max(1, total - 1)


DEFAULT_NUM_PROCESSES = _determine_default_workers()
NUM_PROCESSES = DEFAULT_NUM_PROCESSES


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
    return density_map


def process_single_image(img_path, gt_dir, output_dir):
    """
    Process a single image - designed for multiprocessing
    Returns: (success: bool, people_count: float, error_msg: str)
    """
    try:
        # Load image
        img = Image.open(img_path)
        img_shape = (img.size[1], img.size[0])

        # Find .mat file
        img_name = img_path.stem
        mat_path = gt_dir / f"GT_{img_name}.mat"

        if not mat_path.exists():
            return (False, 0, f"Mat file not found: {mat_path.name}")

        # Generate density map
        density_map = generate_density_map_from_mat(str(mat_path), img_shape)

        # Save as .h5
        output_path = output_dir / f"{img_name}.h5"
        with h5py.File(str(output_path), 'w') as hf:
            hf['density'] = density_map

        return (True, density_map.sum(), None)

    except Exception as e:
        return (False, 0, str(e))


def process_dataset_parallel(part_a_root, output_root, num_processes):
    """Process dataset using multiprocessing for speed"""

    print("="*70)
    print("🚀 OPTIMIZED CSRNet Density Map Generator")
    print(f"   CPU Cores: {num_processes} parallel processes")
    print("="*70)

    stats = {}

    for split in ['train_data', 'test_data']:
        split_name = "train" if "train" in split else "test"

        print(f"\n{'='*70}")
        print(f"📁 Processing {split_name.upper()}ING SET")
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
    print(f"⚡ Processing with {num_processes} parallel workers...\n")

        # Create partial function with fixed arguments
        process_func = partial(process_single_image, 
                              gt_dir=gt_dir, 
                              output_dir=output_dir)

        # Process in parallel with progress bar
        success_count = 0
        total_people = 0
        errors = []

        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=num_processes) as pool:
            results = list(tqdm(
                pool.imap(process_func, img_files, chunksize=2),
                total=len(img_files),
                desc=f"   Generating {split_name} density maps"
            ))

        # Aggregate results
        for (success, people_count, error_msg) in results:
            if success:
                success_count += 1
                total_people += people_count
            else:
                errors.append(error_msg)

        elapsed_time = time.time() - start_time

        # Store statistics
        stats[split_name] = {
            "total": len(img_files),
            "success": success_count,
            "people": int(total_people),
            "avg_count": total_people / success_count if success_count > 0 else 0,
            "time": elapsed_time,
            "speed": len(img_files) / elapsed_time
        }

        print(f"\n✅ Generated: {success_count}/{len(img_files)} density maps")
        print(f"👥 Total people: {int(total_people)}")
        print(f"📈 Average per image: {total_people/success_count:.1f}")
        print(f"⏱️  Time: {elapsed_time:.1f}s ({stats[split_name]['speed']:.2f} images/sec)")
        print(f"📂 Saved to: {output_dir}")

        if errors:
            print(f"\n⚠️  {len(errors)} errors occurred")

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
        print(f"  Speedup vs serial: ~{max(1, num_processes//2)}x - {max(1, int(num_processes//1.5))}x faster")


# =====================================================
# MAIN EXECUTION
# =====================================================
if __name__ == "__main__":
    import argparse

    mp.freeze_support()

    parser = argparse.ArgumentParser(description='Optimized density map generation')
    parser.add_argument('--dataset-root', type=str, 
                       default='D:\\College\\Major Project\\ml\\datasets\\raw\\ShanghaiTech\\ShanghaiTech',
                       help='Root directory of ShanghaiTech dataset')
    parser.add_argument('--output-root', type=str,
                       default='D:\\College\\Major Project\\ml\\datasets\\processed\\shanghaiTech',
                       help='Output directory for density maps')
    parser.add_argument('--processes', type=int,
                       default=DEFAULT_NUM_PROCESSES,
                       help=f'Number of parallel processes (default: {DEFAULT_NUM_PROCESSES})')

    args = parser.parse_args()
    NUM_PROCESSES = max(1, args.processes)

    # Find dataset
    dataset_root = Path(args.dataset_root)
    if not dataset_root.exists():
        print(f"❌ Dataset not found: {dataset_root}")
        exit(1)

    # Find part_A
    part_a_root = dataset_root / "part_A"
    if not part_a_root.exists():
        print(f"❌ Part A not found: {part_a_root}")
        exit(1)

    print(f"� Using {NUM_PROCESSES} CPU cores out of {mp.cpu_count()} available\n")
    print(f"�📂 Dataset: {part_a_root}")
    print(f"📂 Output: {args.output_root}\n")

    # Process dataset
    stats = process_dataset_parallel(part_a_root, args.output_root, NUM_PROCESSES)

    # Verify and summarize
    verify_and_summarize(args.output_root, stats)

    print("\n" + "="*70)
    print("🎉 All Done!")
    print("="*70)
