"""
Visualize Fine-tuning Results

Creates visualizations to show training progress and model performance.
"""

import matplotlib.pyplot as plt
import numpy as np
import torch
import json
import os
from pathlib import Path


def plot_training_history(checkpoint_path, save_path='training_history.png'):
    """Plot training loss and metrics over epochs"""
    
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    
    if 'history' not in checkpoint:
        print("❌ No training history found in checkpoint")
        return
    
    history = checkpoint['history']
    epochs = range(1, len(history['train_loss']) + 1)
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Loss
    axes[0, 0].plot(epochs, history['train_loss'], 'b-', label='Train Loss', linewidth=2)
    axes[0, 0].plot(epochs, history['val_loss'], 'r-', label='Val Loss', linewidth=2)
    axes[0, 0].set_xlabel('Epoch', fontsize=12)
    axes[0, 0].set_ylabel('Loss', fontsize=12)
    axes[0, 0].set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
    axes[0, 0].legend(fontsize=11)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: MAE
    axes[0, 1].plot(epochs, history['train_mae'], 'b-', label='Train MAE', linewidth=2)
    axes[0, 1].plot(epochs, history['val_mae'], 'r-', label='Val MAE', linewidth=2)
    axes[0, 1].set_xlabel('Epoch', fontsize=12)
    axes[0, 1].set_ylabel('MAE', fontsize=12)
    axes[0, 1].set_title('Mean Absolute Error', fontsize=14, fontweight='bold')
    axes[0, 1].legend(fontsize=11)
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: MSE
    axes[1, 0].plot(epochs, history['train_mse'], 'b-', label='Train MSE', linewidth=2)
    axes[1, 0].plot(epochs, history['val_mse'], 'r-', label='Val MSE', linewidth=2)
    axes[1, 0].set_xlabel('Epoch', fontsize=12)
    axes[1, 0].set_ylabel('MSE', fontsize=12)
    axes[1, 0].set_title('Mean Squared Error', fontsize=14, fontweight='bold')
    axes[1, 0].legend(fontsize=11)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Best MAE marker
    best_epoch = np.argmin(history['val_mae']) + 1
    best_mae = min(history['val_mae'])
    
    axes[1, 1].plot(epochs, history['val_mae'], 'r-', linewidth=2)
    axes[1, 1].plot(best_epoch, best_mae, 'g*', markersize=20, label=f'Best: {best_mae:.2f} @ epoch {best_epoch}')
    axes[1, 1].set_xlabel('Epoch', fontsize=12)
    axes[1, 1].set_ylabel('Validation MAE', fontsize=12)
    axes[1, 1].set_title('Validation MAE with Best Model', fontsize=14, fontweight='bold')
    axes[1, 1].legend(fontsize=11)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✅ Saved training history to: {save_path}")
    plt.show()
    
    # Print summary
    print("\n📊 Training Summary:")
    print(f"   Total epochs: {len(epochs)}")
    print(f"   Best validation MAE: {best_mae:.2f} (epoch {best_epoch})")
    print(f"   Final validation MAE: {history['val_mae'][-1]:.2f}")
    print(f"   Improvement: {history['val_mae'][0] - best_mae:.2f}")


def compare_checkpoints(checkpoint_paths, labels, save_path='checkpoint_comparison.png'):
    """Compare multiple checkpoints"""
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    colors = ['b', 'r', 'g', 'orange', 'purple']
    
    for i, (ckpt_path, label) in enumerate(zip(checkpoint_paths, labels)):
        checkpoint = torch.load(ckpt_path, map_location='cpu')
        
        if 'history' not in checkpoint:
            continue
        
        history = checkpoint['history']
        epochs = range(1, len(history['val_mae']) + 1)
        color = colors[i % len(colors)]
        
        # Plot MAE
        axes[0].plot(epochs, history['val_mae'], color=color, label=label, linewidth=2)
        
        # Plot loss
        axes[1].plot(epochs, history['val_loss'], color=color, label=label, linewidth=2)
    
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Validation MAE', fontsize=12)
    axes[0].set_title('Validation MAE Comparison', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Validation Loss', fontsize=12)
    axes[1].set_title('Validation Loss Comparison', fontsize=14, fontweight='bold')
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✅ Saved comparison to: {save_path}")
    plt.show()


def visualize_predictions_grid(model, image_dir, num_images=9, save_path='predictions_grid.png'):
    """Create grid visualization of predictions"""
    import glob
    from PIL import Image
    from torchvision import transforms
    
    image_paths = sorted(glob.glob(os.path.join(image_dir, '*.jpg')))[:num_images]
    
    if len(image_paths) == 0:
        print(f"❌ No images found in {image_dir}")
        return
    
    rows = int(np.sqrt(num_images))
    cols = (num_images + rows - 1) // rows
    
    fig, axes = plt.subplots(rows, cols, figsize=(20, 20))
    axes = axes.flatten() if num_images > 1 else [axes]
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    model.eval()
    
    print(f"Processing {len(image_paths)} images...")
    
    for idx, img_path in enumerate(image_paths):
        # Load image
        img = Image.open(img_path).convert('RGB')
        img_tensor = transform(img).unsqueeze(0).to(device)
        
        # Predict
        with torch.no_grad():
            density = model(img_tensor)
        
        count = density.sum().item()
        density_np = density[0, 0].cpu().numpy()
        
        # Plot
        axes[idx].imshow(np.array(img))
        axes[idx].imshow(density_np, cmap='jet', alpha=0.5)
        axes[idx].set_title(f'{os.path.basename(img_path)}\nCount: {count:.1f}', 
                           fontsize=10, fontweight='bold')
        axes[idx].axis('off')
    
    # Hide extra subplots
    for idx in range(len(image_paths), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✅ Saved predictions grid to: {save_path}")
    plt.show()


def create_error_distribution(results_dict, save_path='error_distribution.png'):
    """Plot error distribution histogram"""
    
    errors = []
    for result in results_dict.values():
        errors.append(abs(result['predicted'] - result['ground_truth']))
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Histogram
    axes[0].hist(errors, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    axes[0].axvline(np.mean(errors), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(errors):.2f}')
    axes[0].axvline(np.median(errors), color='green', linestyle='--', linewidth=2, label=f'Median: {np.median(errors):.2f}')
    axes[0].set_xlabel('Absolute Error', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('Error Distribution', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Scatter plot: GT vs Predicted
    gts = [result['ground_truth'] for result in results_dict.values()]
    preds = [result['predicted'] for result in results_dict.values()]
    
    axes[1].scatter(gts, preds, alpha=0.6, s=50, color='steelblue')
    axes[1].plot([min(gts), max(gts)], [min(gts), max(gts)], 'r--', linewidth=2, label='Perfect prediction')
    axes[1].set_xlabel('Ground Truth Count', fontsize=12)
    axes[1].set_ylabel('Predicted Count', fontsize=12)
    axes[1].set_title('Predicted vs Ground Truth', fontsize=14, fontweight='bold')
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✅ Saved error distribution to: {save_path}")
    plt.show()
    
    # Print statistics
    print("\n📊 Error Statistics:")
    print(f"   Mean Absolute Error: {np.mean(errors):.2f}")
    print(f"   Median Absolute Error: {np.median(errors):.2f}")
    print(f"   Std Dev: {np.std(errors):.2f}")
    print(f"   Min Error: {min(errors):.2f}")
    print(f"   Max Error: {max(errors):.2f}")
    print(f"   25th Percentile: {np.percentile(errors, 25):.2f}")
    print(f"   75th Percentile: {np.percentile(errors, 75):.2f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize fine-tuning results')
    parser.add_argument('--checkpoint', required=True,
                       help='Path to checkpoint with training history')
    parser.add_argument('--output-dir', default='visualizations',
                       help='Directory to save visualizations')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("=" * 70)
    print("🎨 Visualizing Fine-tuning Results")
    print("=" * 70)
    
    # Plot training history
    save_path = os.path.join(args.output_dir, 'training_history.png')
    plot_training_history(args.checkpoint, save_path)
    
    print("\n" + "=" * 70)
    print("🎉 Done! Check the visualizations in:", args.output_dir)
    print("=" * 70)
