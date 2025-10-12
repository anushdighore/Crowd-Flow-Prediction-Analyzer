"""
CSRNet Evaluation Script
Evaluate trained CSRNet model on test set and generate visualizations
"""
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import yaml
from tqdm import tqdm
import sys
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from ml.src.models.csrnet.csrnet import load_csrnet
from ml.src.csrnet.training.dataset import ShanghaiTechPartA


class CSRNetEvaluator:
    """Evaluator for CSRNet model"""
    
    def __init__(self, checkpoint_path, config_path='ml/csrnet_config.yaml'):
        """
        Initialize evaluator
        
        Args:
            checkpoint_path: Path to model checkpoint
            config_path: Path to training configuration
        """
        self.checkpoint_path = checkpoint_path
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Setup device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🖥️  Device: {self.device}")
        
        # Load model
        print(f"📥 Loading checkpoint: {checkpoint_path}")
        self.model = load_csrnet(checkpoint_path, device=str(self.device))
        self.model.eval()
        
        # Setup data
        dataset_config = self.config['training']['dataset']
        self.data = ShanghaiTechPartA(
            dataset_root=dataset_config['dataset_root'],
            density_root=dataset_config['density_root'],
            batch_size=1,  # Evaluate one image at a time
            num_workers=0,
            augment_train=False
        )
        
        self.test_loader = self.data.get_test_loader()
        print(f"📁 Test images: {len(self.test_loader)}")
        
        # Loss function
        self.criterion = nn.MSELoss()
    
    @torch.no_grad()
    def evaluate(self):
        """Evaluate model on test set"""
        print("\n🔍 Evaluating model...")
        
        all_predictions = []
        all_ground_truths = []
        total_loss = 0.0
        
        for images, targets, counts in tqdm(self.test_loader, desc="Evaluating"):
            # Move to device
            images = images.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            outputs = self.model(images)
            
            # Calculate loss
            loss = self.criterion(outputs, targets)
            total_loss += loss.item()
            
            # Get predicted count
            pred_count = outputs.sum().item()
            true_count = counts.item()
            
            all_predictions.append(pred_count)
            all_ground_truths.append(true_count)
        
        # Convert to numpy arrays
        predictions = np.array(all_predictions)
        ground_truths = np.array(all_ground_truths)
        
        # Calculate metrics
        mae = np.abs(predictions - ground_truths).mean()
        mse = ((predictions - ground_truths) ** 2).mean()
        rmse = np.sqrt(mse)
        avg_loss = total_loss / len(self.test_loader)
        
        # Calculate relative error
        relative_errors = np.abs(predictions - ground_truths) / (ground_truths + 1e-6)
        mean_relative_error = relative_errors.mean()
        
        # Print results
        print("\n" + "="*60)
        print("📊 EVALUATION RESULTS")
        print("="*60)
        print(f"Test Loss: {avg_loss:.4f}")
        print(f"MAE (Mean Absolute Error): {mae:.2f}")
        print(f"MSE (Mean Squared Error): {mse:.2f}")
        print(f"RMSE (Root Mean Squared Error): {rmse:.2f}")
        print(f"Mean Relative Error: {mean_relative_error*100:.2f}%")
        print("="*60)
        
        return {
            'predictions': predictions,
            'ground_truths': ground_truths,
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'loss': avg_loss,
            'relative_error': mean_relative_error
        }
    
    def visualize_results(self, results, output_dir='ml/src/csrnet/training/logs/evaluation'):
        """
        Create visualization plots
        
        Args:
            results: Dictionary with evaluation results
            output_dir: Directory to save plots
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        predictions = results['predictions']
        ground_truths = results['ground_truths']
        
        # 1. Scatter plot: Predicted vs Ground Truth
        plt.figure(figsize=(10, 8))
        plt.scatter(ground_truths, predictions, alpha=0.5)
        plt.plot([ground_truths.min(), ground_truths.max()], 
                [ground_truths.min(), ground_truths.max()], 
                'r--', label='Perfect Prediction')
        plt.xlabel('Ground Truth Count')
        plt.ylabel('Predicted Count')
        plt.title(f'Predictions vs Ground Truth\nMAE: {results["mae"]:.2f}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'scatter_plot.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Error distribution
        errors = predictions - ground_truths
        plt.figure(figsize=(10, 6))
        plt.hist(errors, bins=50, edgecolor='black')
        plt.xlabel('Prediction Error')
        plt.ylabel('Frequency')
        plt.title(f'Error Distribution\nMean: {errors.mean():.2f}, Std: {errors.std():.2f}')
        plt.axvline(0, color='r', linestyle='--', label='Zero Error')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'error_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Absolute error distribution
        abs_errors = np.abs(errors)
        plt.figure(figsize=(10, 6))
        plt.hist(abs_errors, bins=50, edgecolor='black')
        plt.xlabel('Absolute Error')
        plt.ylabel('Frequency')
        plt.title(f'Absolute Error Distribution\nMAE: {results["mae"]:.2f}')
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'abs_error_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Error vs Ground Truth
        plt.figure(figsize=(10, 6))
        plt.scatter(ground_truths, abs_errors, alpha=0.5)
        plt.xlabel('Ground Truth Count')
        plt.ylabel('Absolute Error')
        plt.title('Absolute Error vs Ground Truth Count')
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'error_vs_gt.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n📊 Visualizations saved to: {output_dir}")
    
    def visualize_sample_predictions(self, num_samples=5, output_dir='ml/src/csrnet/training/logs/evaluation/samples'):
        """
        Visualize density map predictions for sample images
        
        Args:
            num_samples: Number of samples to visualize
            output_dir: Directory to save visualizations
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n🖼️  Generating {num_samples} sample visualizations...")
        
        # Get dataset without data loader
        dataset = self.data.get_test_loader().dataset
        
        # Select random samples
        indices = np.random.choice(len(dataset), min(num_samples, len(dataset)), replace=False)
        
        for idx in indices:
            # Get data
            img_tensor, target, true_count = dataset[idx]
            
            # Predict
            img_tensor = img_tensor.unsqueeze(0).to(self.device)
            with torch.no_grad():
                pred_density = self.model(img_tensor)
            
            # Convert to numpy
            pred_density = pred_density.squeeze().cpu().numpy()
            target = target.squeeze().cpu().numpy()
            
            pred_count = pred_density.sum()
            
            # Denormalize image for visualization
            img = img_tensor.squeeze().cpu().numpy()
            img = img.transpose(1, 2, 0)
            img = img * np.array([0.229, 0.224, 0.225]) + np.array([0.485, 0.456, 0.406])
            img = np.clip(img, 0, 1)
            
            # Create visualization
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Original image
            axes[0].imshow(img)
            axes[0].set_title(f'Original Image\nTrue Count: {true_count:.0f}')
            axes[0].axis('off')
            
            # Ground truth density map
            im1 = axes[1].imshow(target, cmap='jet')
            axes[1].set_title(f'Ground Truth Density\nCount: {true_count:.0f}')
            axes[1].axis('off')
            plt.colorbar(im1, ax=axes[1])
            
            # Predicted density map
            im2 = axes[2].imshow(pred_density, cmap='jet')
            axes[2].set_title(f'Predicted Density\nCount: {pred_count:.0f}\nError: {abs(pred_count - true_count):.0f}')
            axes[2].axis('off')
            plt.colorbar(im2, ax=axes[2])
            
            plt.tight_layout()
            plt.savefig(output_dir / f'sample_{idx}.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"📊 Sample visualizations saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Evaluate CSRNet model')
    parser.add_argument('--checkpoint', type=str, required=True,
                       help='Path to model checkpoint')
    parser.add_argument('--config', type=str, default='ml/csrnet_config.yaml',
                       help='Path to training configuration')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualization plots')
    parser.add_argument('--samples', type=int, default=5,
                       help='Number of sample predictions to visualize')
    
    args = parser.parse_args()
    
    # Create evaluator
    evaluator = CSRNetEvaluator(args.checkpoint, args.config)
    
    # Evaluate
    results = evaluator.evaluate()
    
    # Visualize
    if args.visualize:
        evaluator.visualize_results(results)
        evaluator.visualize_sample_predictions(num_samples=args.samples)
    
    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()
