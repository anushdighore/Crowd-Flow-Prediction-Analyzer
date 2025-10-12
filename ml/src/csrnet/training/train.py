"""
CSRNet Training Script for ShanghaiTech Part A
Fine-tuning CSRNet on crowd counting dataset
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard.writer import SummaryWriter
from torch.cuda.amp import autocast, GradScaler
import yaml
import argparse
from pathlib import Path
import time
import logging
from tqdm import tqdm
import sys
import numpy as np
from typing import Union

# Add project root to path (repo root)
# __file__ = ml/src/csrnet/training/train.py
# parents: [0]=training, [1]=csrnet, [2]=src, [3]=ml, [4]=repo_root
project_root = Path(__file__).parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def _resolve_path(p: Union[str, Path]) -> Path:
    pth = Path(p)
    return pth if pth.is_absolute() else (project_root / pth)

from ml.datasets.utils.csrnet.csrnet import CSRNet, load_csrnet
from ml.src.csrnet.training.dataset import ShanghaiTechPartA


class CSRNetTrainer:
    """Trainer class for CSRNet fine-tuning"""
    
    def __init__(self, config_path='ml/csrnet_config.yaml'):
        """
        Initialize trainer
        
        Args:
            config_path: Path to training configuration file
        """
        # Load configuration (support relative path from repo root)
        cfg_path = _resolve_path(config_path)
        with open(cfg_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Setup device
        self.device = torch.device('cuda' if torch.cuda.is_available() and self.config['device']['cuda'] else 'cpu')
        print(f"🖥️  Device: {self.device}")
        
        # Setup logging
        self.setup_logging()
        
        # Setup model
        self.setup_model()
        
        # Setup data
        self.setup_data()
        
        # Setup training components
        self.setup_training()
        
        # Setup checkpointing
        self.setup_checkpointing()
        
        # Setup mixed precision training
        self.setup_amp()
        
        # Training state
        self.current_epoch = 0
        self.best_val_loss = float('inf')
        self.epochs_without_improvement = 0
    
    def setup_logging(self):
        """Setup logging and TensorBoard"""
        log_config = self.config['logging']
        
        # Create log directory
        log_dir = _resolve_path(log_config['log_dir'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup file logging
        log_file = log_dir / log_config['file']['log_file']
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting CSRNet training")
        
        # Setup TensorBoard
        if log_config['tensorboard']['enabled']:
            tb_dir = _resolve_path(log_config['tensorboard']['log_dir'])
            tb_dir.mkdir(parents=True, exist_ok=True)
            self.writer = SummaryWriter(log_dir=str(tb_dir))
            self.logger.info(f"TensorBoard: {tb_dir}")
        else:
            self.writer = None
    
    def setup_model(self):
        """Setup CSRNet model"""
        model_config = self.config['model']
        
        if model_config['load_pretrained'] and model_config['pretrained_checkpoint']:
            # Load from checkpoint
            checkpoint_path = _resolve_path(model_config['pretrained_checkpoint'])
            if checkpoint_path.exists():
                self.logger.info(f"Loading checkpoint: {checkpoint_path}")
                self.model = load_csrnet(str(checkpoint_path), device=str(self.device))
            else:
                self.logger.warning(f"Pretrained checkpoint not found at {checkpoint_path}. Proceeding with randomly initialized CSRNet.")
                self.model = CSRNet(load_weights=False).to(self.device)
        else:
            # Create new model with VGG16 initialization
            self.logger.info("Creating new CSRNet model")
            self.model = CSRNet(load_weights=False)
            self.model = self.model.to(self.device)
        
        # Count parameters
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        self.logger.info(f"Total parameters: {total_params:,}")
        self.logger.info(f"Trainable parameters: {trainable_params:,}")
    
    def setup_data(self):
        """Setup data loaders"""
        dataset_config = self.config['training']['dataset']
        dataloader_config = self.config['training']['dataloader']
        
        self.data = ShanghaiTechPartA(
            dataset_root=str(_resolve_path(dataset_config['dataset_root'])),
            density_root=str(_resolve_path(dataset_config['density_root'])),
            batch_size=self.config['training']['hyperparameters']['batch_size'],
            num_workers=dataloader_config['num_workers'],
            augment_train=self.config['training']['augmentation']['enabled']
        )
        
        self.train_loader = self.data.get_train_loader()
        self.test_loader = self.data.get_test_loader()
        
        self.logger.info(f"Train batches: {len(self.train_loader)}")
        self.logger.info(f"Test batches: {len(self.test_loader)}")
    
    def setup_training(self):
        """Setup optimizer, loss, and scheduler"""
        hp = self.config['training']['hyperparameters']
        
        # Loss function
        self.criterion = nn.MSELoss()
        
        # Optimizer
        if hp['optimizer'] == 'adam':
            self.optimizer = optim.Adam(
                self.model.parameters(),
                lr=hp['learning_rate'],
                weight_decay=hp['weight_decay'],
                **hp['optimizer_params']
            )
        else:
            raise ValueError(f"Unsupported optimizer: {hp['optimizer']}")
        
        # Learning rate scheduler
        if hp['lr_scheduler'] == 'step':
            self.scheduler = optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=hp['lr_step_size'],
                gamma=hp['lr_gamma']
            )
        else:
            self.scheduler = None
        
        self.logger.info(f"Optimizer: {hp['optimizer']}, LR: {hp['learning_rate']}")
    
    def setup_checkpointing(self):
        """Setup checkpoint directory"""
        ckpt_config = self.config['checkpointing']
        self.checkpoint_dir = _resolve_path(ckpt_config['save_dir'])
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Checkpoints: {self.checkpoint_dir}")
    
    def setup_amp(self):
        """Setup automatic mixed precision training"""
        hp = self.config['training']['hyperparameters']
        self.use_amp = hp.get('use_amp', True) and self.device.type == 'cuda'
        self.accumulate_grad_batches = hp.get('accumulate_grad_batches', 1)
        
        if self.use_amp:
            self.scaler = GradScaler()
            self.logger.info("Mixed precision training enabled (FP16)")
        else:
            self.scaler = None
            self.logger.info("Mixed precision training disabled (FP32)")
        
        if self.accumulate_grad_batches > 1:
            effective_batch = self.config['training']['hyperparameters']['batch_size'] * self.accumulate_grad_batches
            self.logger.info(f"Gradient accumulation: {self.accumulate_grad_batches} steps (effective batch_size={effective_batch})")
        
        # Debug: Verify DataLoader optimization settings
        self.logger.info(f"DataLoader: workers={self.train_loader.num_workers}, pin={self.train_loader.pin_memory}, persistent={self.train_loader.persistent_workers}, prefetch={self.train_loader.prefetch_factor}")
    
    def train_epoch(self):
        """Train for one epoch"""
        self.model.train()
        epoch_loss = 0.0
        epoch_mae = 0.0
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {self.current_epoch + 1}")
        
        for batch_idx, (images, targets, counts) in enumerate(pbar):
            # Move to device
            images = images.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            
            # Forward pass with mixed precision
            if self.use_amp:
                with autocast():
                    outputs = self.model(images)
                    loss = self.criterion(outputs, targets) / self.accumulate_grad_batches
                
                # Scaled backward pass
                self.scaler.scale(loss).backward()
            else:
                # Standard FP32
                outputs = self.model(images)
                loss = self.criterion(outputs, targets) / self.accumulate_grad_batches
                loss.backward()
            
            # Update weights only every N batches (gradient accumulation)
            if (batch_idx + 1) % self.accumulate_grad_batches == 0:
                if self.use_amp:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()
                self.optimizer.zero_grad()
            
            # Calculate MAE (detach to avoid keeping computation graph)
            with torch.no_grad():
                pred_counts = outputs.sum(dim=(1, 2, 3)).cpu().numpy()
                true_counts = counts.numpy()
                mae = np.abs(pred_counts - true_counts).mean()
            
            # Free up memory after calculations
            del outputs, images, targets
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            
            # Update metrics (scale loss back for logging)
            epoch_loss += loss.item() * self.accumulate_grad_batches
            epoch_mae += mae
            
            # Update progress bar
            pbar.set_postfix({
                'loss': loss.item() * self.accumulate_grad_batches,
                'mae': mae
            })
            
            # Log to TensorBoard (only on actual weight updates)
            if self.writer and (batch_idx + 1) % self.accumulate_grad_batches == 0:
                if batch_idx % self.config['logging']['console']['log_every_n_batches'] == 0:
                    global_step = self.current_epoch * len(self.train_loader) + batch_idx
                    self.writer.add_scalar('train/batch_loss', loss.item() * self.accumulate_grad_batches, global_step)
                    self.writer.add_scalar('train/batch_mae', mae, global_step)
        
        # Handle remaining batches at epoch end
        if (batch_idx + 1) % self.accumulate_grad_batches != 0:
            if self.use_amp:
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                self.optimizer.step()
            self.optimizer.zero_grad()
        
        # Average metrics
        avg_loss = epoch_loss / len(self.train_loader)
        avg_mae = epoch_mae / len(self.train_loader)
        
        return avg_loss, avg_mae
    
    @torch.no_grad()
    def validate(self):
        """Validate on test set"""
        self.model.eval()
        val_loss = 0.0
        val_mae = 0.0
        val_mse = 0.0
        
        for images, targets, counts in tqdm(self.test_loader, desc="Validating"):
            # Move to device
            images = images.to(self.device, non_blocking=True)
            targets = targets.to(self.device, non_blocking=True)
            
            # Forward pass with mixed precision
            if self.use_amp:
                with autocast():
                    outputs = self.model(images)
                    loss = self.criterion(outputs, targets)
            else:
                outputs = self.model(images)
                loss = self.criterion(outputs, targets)
            
            val_loss += loss.item()
            
            # Calculate metrics
            pred_counts = outputs.sum(dim=(1, 2, 3)).cpu().numpy()
            true_counts = counts.numpy()
            
            mae = np.abs(pred_counts - true_counts).mean()
            mse = ((pred_counts - true_counts) ** 2).mean()
            
            val_mae += mae
            val_mse += mse
        
        # Average metrics
        avg_loss = val_loss / len(self.test_loader)
        avg_mae = val_mae / len(self.test_loader)
        avg_mse = val_mse / len(self.test_loader)
        avg_rmse = np.sqrt(avg_mse)
        
        return avg_loss, avg_mae, avg_mse, avg_rmse
    
    def save_checkpoint(self, epoch, loss, is_best=False):
        """Save model checkpoint"""
        ckpt_config = self.config['checkpointing']
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': loss,
            'best_val_loss': self.best_val_loss,
            'config': self.config
        }
        
        if self.scheduler:
            checkpoint['scheduler_state_dict'] = self.scheduler.state_dict()
        
        # Save regular checkpoint
        if ckpt_config['save_frequency'] > 0 and epoch % ckpt_config['save_frequency'] == 0:
            filename = ckpt_config['checkpoint_pattern'].format(epoch=epoch, loss=loss)
            filepath = self.checkpoint_dir / filename
            torch.save(checkpoint, filepath)
            self.logger.info(f"Saved checkpoint: {filename}")
        
        # Save best checkpoint
        if is_best and ckpt_config['save_best']:
            best_path = self.checkpoint_dir / ckpt_config['best_checkpoint_name']
            torch.save(checkpoint, best_path)
            self.logger.info(f"Saved best checkpoint: {ckpt_config['best_checkpoint_name']}")
    
    def train(self):
        """Main training loop"""
        hp = self.config['training']['hyperparameters']
        val_config = self.config['validation']
        
        num_epochs = hp['epochs']
        self.logger.info(f"Training for {num_epochs} epochs")
        
        # Get dataset size for performance tracking
        train_dataset_size = len(self.train_loader.dataset) if hasattr(self.train_loader, 'dataset') else len(self.train_loader) * hp['batch_size']
        
        for epoch in range(num_epochs):
            self.current_epoch = epoch
            epoch_start_time = time.time()
            
            # Train
            train_loss, train_mae = self.train_epoch()
            
            # Calculate epoch time and throughput
            epoch_time = time.time() - epoch_start_time
            samples_per_sec = train_dataset_size / epoch_time if epoch_time > 0 else 0
            
            # Learning rate step
            if self.scheduler:
                self.scheduler.step()
                current_lr = self.scheduler.get_last_lr()[0]
            else:
                current_lr = hp['learning_rate']
            
            # Validate
            should_validate = (epoch + 1) % val_config['validate_every'] == 0
            if should_validate:
                val_loss, val_mae, val_mse, val_rmse = self.validate()
                
                # Check if best model
                is_best = val_loss < self.best_val_loss
                if is_best:
                    self.best_val_loss = val_loss
                    self.epochs_without_improvement = 0
                else:
                    self.epochs_without_improvement += 1
                
                # Log validation metrics
                self.logger.info(
                    f"Epoch {epoch + 1}/{num_epochs} - "
                    f"Train Loss: {train_loss:.4f}, Train MAE: {train_mae:.2f} - "
                    f"Val Loss: {val_loss:.4f}, Val MAE: {val_mae:.2f}, Val RMSE: {val_rmse:.2f} - "
                    f"Time: {epoch_time:.1f}s, Throughput: {samples_per_sec:.1f} samples/s"
                )
                
                # TensorBoard logging
                if self.writer:
                    self.writer.add_scalar('val/loss', val_loss, epoch)
                    self.writer.add_scalar('val/mae', val_mae, epoch)
                    self.writer.add_scalar('val/mse', val_mse, epoch)
                    self.writer.add_scalar('val/rmse', val_rmse, epoch)
                
                # Save checkpoint
                self.save_checkpoint(epoch + 1, val_loss, is_best=is_best)
                
                # Early stopping check
                if val_config['early_stopping']['enabled']:
                    patience = val_config['early_stopping']['patience']
                    if self.epochs_without_improvement >= patience:
                        self.logger.info(f"Early stopping triggered after {patience} epochs without improvement")
                        break
            else:
                self.logger.info(
                    f"Epoch {epoch + 1}/{num_epochs} - "
                    f"Train Loss: {train_loss:.4f}, Train MAE: {train_mae:.2f} - "
                    f"Time: {epoch_time:.1f}s, Throughput: {samples_per_sec:.1f} samples/s"
                )
            
            # TensorBoard logging
            if self.writer:
                self.writer.add_scalar('train/loss', train_loss, epoch)
                self.writer.add_scalar('train/mae', train_mae, epoch)
                self.writer.add_scalar('train/lr', current_lr, epoch)
                self.writer.add_scalar('performance/epoch_time_sec', epoch_time, epoch)
                self.writer.add_scalar('performance/samples_per_sec', samples_per_sec, epoch)
        
        self.logger.info("Training complete!")
        self.logger.info(f"Best validation loss: {self.best_val_loss:.4f}")
        
        if self.writer:
            self.writer.close()


def main():
    parser = argparse.ArgumentParser(description='Train CSRNet on ShanghaiTech Part A')
    parser.add_argument('--config', type=str, default='ml/csrnet_config.yaml',
                       help='Path to training configuration file')
    parser.add_argument('--epochs', type=int, default=None,
                       help='Override number of epochs from config (optional)')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = CSRNetTrainer(config_path=args.config)
    # Optional override of epochs for quick smoke tests
    if args.epochs is not None:
        trainer.config['training']['hyperparameters']['epochs'] = int(args.epochs)
    
    # Start training
    trainer.train()


if __name__ == "__main__":
    main()
