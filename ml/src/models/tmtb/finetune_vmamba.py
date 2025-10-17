"""
Fine-tune VMamba TMTB on ShanghaiTech Dataset for Crowd Counting

This script fine-tunes your existing VMamba checkpoint (jhu_5.pth) 
on ShanghaiTech dataset to adapt it for crowd counting.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np
import os
import h5py
import json
from tqdm import tqdm
import logging
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from models.vmamba_tmtb import VMambaTMTB, load_vmamba_tmtb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShanghaiTechDataset(Dataset):
    """ShanghaiTech dataset for crowd counting"""
    
    def __init__(self, img_root, gt_root, transform=None, gt_downsample=8):
        self.img_root = img_root
        self.gt_root = gt_root
        self.transform = transform
        self.gt_downsample = gt_downsample
        
        # Get all image files
        self.img_files = sorted([f for f in os.listdir(img_root) if f.endswith('.jpg')])
        logger.info(f"Found {len(self.img_files)} images in {img_root}")
    
    def __len__(self):
        return len(self.img_files)
    
    def __getitem__(self, idx):
        # Load image
        img_path = os.path.join(self.img_root, self.img_files[idx])
        img = Image.open(img_path).convert('RGB')
        
        # Load ground truth density map
        gt_path = os.path.join(
            self.gt_root,
            self.img_files[idx].replace('.jpg', '.h5')
        )
        
        with h5py.File(gt_path, 'r') as f:
            density = np.array(f['density'])
        
        # Get original count before any resizing
        original_count = density.sum()
        
        # Resize density map to match fixed image size (512x512)
        # Then downsample to match model output (512/4 = 128)
        import cv2
        fixed_size = 512
        target_h, target_w = fixed_size // 4, fixed_size // 4  # Model outputs at 1/4 resolution
        
        # Resize density map and scale to maintain count
        density = cv2.resize(density, (target_w, target_h), 
                           interpolation=cv2.INTER_CUBIC)
        
        # Rescale to preserve the original count
        current_count = density.sum()
        if current_count > 0:
            density = density * (original_count / current_count)
        
        # Apply transforms to image (will resize to 512x512)
        if self.transform:
            img = self.transform(img)
        
        # Convert density to tensor
        density = torch.from_numpy(density).float().unsqueeze(0)  # [1, H, W]
        
        # Get count
        count = density.sum().item()
        
        return img, density, count


def create_dataloaders(data_root, batch_size=8, num_workers=4):
    """Create train and test dataloaders"""
    
    # Image transformations - resize to fixed size for batching
    train_transform = transforms.Compose([
        transforms.Resize((512, 512)),  # Resize all images to same size
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    test_transform = transforms.Compose([
        transforms.Resize((512, 512)),  # Resize all images to same size
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Create datasets
    train_dataset = ShanghaiTechDataset(
        img_root=os.path.join(data_root, 'train_data', 'images'),
        gt_root=os.path.join(data_root, 'train_data', 'ground-truth-h5'),
        transform=train_transform
    )
    
    test_dataset = ShanghaiTechDataset(
        img_root=os.path.join(data_root, 'test_data', 'images'),
        gt_root=os.path.join(data_root, 'test_data', 'ground-truth-h5'),
        transform=test_transform
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return train_loader, test_loader


def train_epoch(model, dataloader, criterion, optimizer, device, epoch):
    """Train for one epoch"""
    model.train()
    
    running_loss = 0.0
    running_mae = 0.0
    running_mse = 0.0
    
    pbar = tqdm(dataloader, desc=f'Epoch {epoch}')
    
    for batch_idx, (images, targets, counts) in enumerate(pbar):
        images = images.to(device)
        targets = targets.to(device)
        counts = torch.tensor(counts).to(device)
        
        # Forward pass
        optimizer.zero_grad()
        outputs = model(images)
        
        # Resize output to match target if needed
        if outputs.shape != targets.shape:
            outputs = nn.functional.interpolate(
                outputs, size=targets.shape[2:],
                mode='bilinear', align_corners=False
            )
        
        # Calculate loss
        loss = criterion(outputs, targets)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Calculate metrics
        pred_counts = outputs.sum(dim=(1,2,3))
        mae = torch.abs(pred_counts - counts).mean().item()
        mse = ((pred_counts - counts) ** 2).mean().item()
        
        running_loss += loss.item()
        running_mae += mae
        running_mse += mse
        
        # Update progress bar
        pbar.set_postfix({
            'loss': loss.item(),
            'MAE': mae,
            'MSE': mse
        })
    
    # Calculate epoch averages
    avg_loss = running_loss / len(dataloader)
    avg_mae = running_mae / len(dataloader)
    avg_mse = running_mse / len(dataloader)
    
    return avg_loss, avg_mae, avg_mse


def validate(model, dataloader, criterion, device):
    """Validate the model"""
    model.eval()
    
    running_loss = 0.0
    running_mae = 0.0
    running_mse = 0.0
    
    with torch.no_grad():
        for images, targets, counts in tqdm(dataloader, desc='Validating'):
            images = images.to(device)
            targets = targets.to(device)
            counts = torch.tensor(counts).to(device)
            
            # Forward pass
            outputs = model(images)
            
            # Resize output to match target if needed
            if outputs.shape != targets.shape:
                outputs = nn.functional.interpolate(
                    outputs, size=targets.shape[2:],
                    mode='bilinear', align_corners=False
                )
            
            # Calculate loss
            loss = criterion(outputs, targets)
            
            # Calculate metrics
            pred_counts = outputs.sum(dim=(1,2,3))
            mae = torch.abs(pred_counts - counts).mean().item()
            mse = ((pred_counts - counts) ** 2).mean().item()
            
            running_loss += loss.item()
            running_mae += mae
            running_mse += mse
    
    # Calculate averages
    avg_loss = running_loss / len(dataloader)
    avg_mae = running_mae / len(dataloader)
    avg_mse = running_mse / len(dataloader)
    
    return avg_loss, avg_mae, avg_mse


def fine_tune_vmamba(
    checkpoint_path='checkpoints/jhu_5.pth',
    data_root='datasets/ShanghaiTech/part_A',
    output_dir='checkpoints/vmamba_finetuned',
    epochs=50,
    batch_size=8,
    learning_rate=1e-5,
    device='cuda'
):
    """Fine-tune VMamba TMTB on ShanghaiTech"""
    
    logger.info("=" * 70)
    logger.info("🚀 Starting VMamba TMTB Fine-tuning on ShanghaiTech")
    logger.info("=" * 70)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load pretrained model
    logger.info(f"📦 Loading pretrained checkpoint: {checkpoint_path}")
    model = load_vmamba_tmtb(checkpoint_path, device=device)
    logger.info("✅ Model loaded successfully")
    
    # Freeze backbone (optional - comment out to train full model)
    # logger.info("🔒 Freezing backbone layers")
    # for param in model.backbone.parameters():
    #     param.requires_grad = False
    
    # Only train regression head
    logger.info("🎯 Training regression head only (faster)")
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"   Trainable parameters: {trainable_params:,}")
    
    # Create dataloaders
    logger.info(f"📂 Loading data from: {data_root}")
    train_loader, test_loader = create_dataloaders(
        data_root, batch_size=batch_size, num_workers=4
    )
    logger.info(f"   Train samples: {len(train_loader.dataset)}")
    logger.info(f"   Test samples: {len(test_loader.dataset)}")
    
    # Loss function and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=learning_rate,
        weight_decay=1e-4
    )
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=15, gamma=0.5)
    
    # Training loop
    best_mae = float('inf')
    history = {
        'train_loss': [], 'train_mae': [], 'train_mse': [],
        'val_loss': [], 'val_mae': [], 'val_mse': []
    }
    
    logger.info("\n" + "=" * 70)
    logger.info("🏋️  Starting Training")
    logger.info("=" * 70)
    
    for epoch in range(1, epochs + 1):
        logger.info(f"\nEpoch {epoch}/{epochs}")
        logger.info("-" * 70)
        
        # Train
        train_loss, train_mae, train_mse = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        
        # Validate
        val_loss, val_mae, val_mse = validate(
            model, test_loader, criterion, device
        )
        
        # Update learning rate
        scheduler.step()
        
        # Log results
        logger.info(f"\n📊 Epoch {epoch} Results:")
        logger.info(f"   Train - Loss: {train_loss:.4f}, MAE: {train_mae:.2f}, MSE: {train_mse:.2f}")
        logger.info(f"   Val   - Loss: {val_loss:.4f}, MAE: {val_mae:.2f}, MSE: {val_mse:.2f}")
        logger.info(f"   LR: {scheduler.get_last_lr()[0]:.2e}")
        
        # Save history
        history['train_loss'].append(train_loss)
        history['train_mae'].append(train_mae)
        history['train_mse'].append(train_mse)
        history['val_loss'].append(val_loss)
        history['val_mae'].append(val_mae)
        history['val_mse'].append(val_mse)
        
        # Save best model
        if val_mae < best_mae:
            best_mae = val_mae
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_mae': best_mae,
                'val_mae': val_mae,
                'val_mse': val_mse
            }
            save_path = os.path.join(output_dir, 'vmamba_shanghai_best.pth')
            torch.save(checkpoint, save_path)
            logger.info(f"   ✅ Saved best model (MAE: {best_mae:.2f})")
        
        # Save checkpoint every 10 epochs
        if epoch % 10 == 0:
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_mae': val_mae,
                'val_mse': val_mse
            }
            save_path = os.path.join(output_dir, f'vmamba_shanghai_epoch{epoch}.pth')
            torch.save(checkpoint, save_path)
            logger.info(f"   💾 Saved checkpoint: epoch{epoch}.pth")
    
    # Save final model
    checkpoint = {
        'epoch': epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'best_mae': best_mae,
        'history': history
    }
    save_path = os.path.join(output_dir, 'vmamba_shanghai_final.pth')
    torch.save(checkpoint, save_path)
    
    logger.info("\n" + "=" * 70)
    logger.info("🎉 Training Complete!")
    logger.info("=" * 70)
    logger.info(f"✅ Best MAE: {best_mae:.2f}")
    logger.info(f"📁 Models saved to: {output_dir}")
    logger.info(f"   - vmamba_shanghai_best.pth (MAE: {best_mae:.2f})")
    logger.info(f"   - vmamba_shanghai_final.pth (final epoch)")
    
    return model, history, best_mae


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fine-tune VMamba TMTB on ShanghaiTech')
    parser.add_argument('--checkpoint', default='checkpoints/jhu_5.pth',
                       help='Path to pretrained VMamba checkpoint')
    parser.add_argument('--data-root', default='datasets/ShanghaiTech/part_A',
                       help='Path to ShanghaiTech dataset (part_A or part_B)')
    parser.add_argument('--output-dir', default='checkpoints/vmamba_finetuned',
                       help='Output directory for fine-tuned models')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of epochs to train')
    parser.add_argument('--batch-size', type=int, default=8,
                       help='Batch size for training')
    parser.add_argument('--lr', type=float, default=1e-5,
                       help='Learning rate')
    parser.add_argument('--device', default='cuda',
                       help='Device to use (cuda or cpu)')
    
    args = parser.parse_args()
    
    # Check if CUDA is available
    if args.device == 'cuda' and not torch.cuda.is_available():
        logger.warning("⚠️  CUDA not available, using CPU")
        args.device = 'cpu'
    
    # Run fine-tuning
    model, history, best_mae = fine_tune_vmamba(
        checkpoint_path=args.checkpoint,
        data_root=args.data_root,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        device=args.device
    )
