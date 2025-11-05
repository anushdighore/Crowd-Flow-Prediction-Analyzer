# Training Guide

Complete guide to training and fine-tuning models in the Multi-Model Crowd Counting System.

## Dataset Preparation

### Download Datasets

#### ShanghaiTech Dataset

```bash
# Download from official source
# https://github.com/desenzhou/ShanghaiTechDataset

mkdir -p ml/datasets/shanghaitech
cd ml/datasets/shanghaitech

# Extract to:
# part_A/train_data/images/
# part_A/test_data/images/
# part_B/train_data/images/
# part_B/test_data/images/
```

#### Other Datasets

- **UCF_CC_50**: Small dataset (50 images)
- **WorldExpo'10**: Single camera scene
- **UCSD**: Sparse crowd dataset

### Dataset Structure

```
datasets/
├── shanghaitech/
│   ├── part_A/
│   │   ├── train_data/
│   │   │   ├── images/
│   │   │   └── ground-truth/
│   │   └── test_data/
│   │       ├── images/
│   │       └── ground-truth/
│   └── part_B/
│       ├── train_data/
│       ├── test_data/
│       ...
├── preprocessing/
│   ├── density_maps/
│   ├── count_labels/
│   └── metadata/
```

### Preprocess Dataset

```python
# ml/src/data/preprocessing.py
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
import json

def generate_density_map(image_path, points, sigma=15):
    """Generate density map from crowd points"""
    
    image = cv2.imread(image_path, 0)
    h, w = image.shape
    
    # Create density map
    density = np.zeros((h, w))
    
    for point in points:
        if 0 <= point[0] < w and 0 <= point[1] < h:
            density[int(point[1]), int(point[0])] += 1
    
    # Apply Gaussian filter
    density = gaussian_filter(density, sigma=sigma)
    
    return density

def preprocess_dataset(dataset_path, output_path):
    """Preprocess entire dataset"""
    
    import os
    from pathlib import Path
    
    os.makedirs(output_path, exist_ok=True)
    
    for image_file in os.listdir(os.path.join(dataset_path, 'images')):
        image_path = os.path.join(dataset_path, 'images', image_file)
        points_file = image_file.replace('.jpg', '.txt')
        points_path = os.path.join(dataset_path, 'ground-truth', points_file)
        
        # Load points
        points = []
        if os.path.exists(points_path):
            with open(points_path) as f:
                for line in f:
                    x, y = map(float, line.strip().split(','))
                    points.append([x, y])
        
        # Generate density map
        density = generate_density_map(image_path, points)
        
        # Save
        output_file = os.path.join(output_path, image_file.replace('.jpg', '.npy'))
        np.save(output_file, density)
        
        print(f"Processed: {image_file}, Count: {len(points)}")

# Run preprocessing
preprocess_dataset('ml/datasets/shanghaitech/part_A/train_data', 
                   'ml/datasets/shanghaitech/processed/part_A/train_data')
```

## CSRNet Training

### Training Configuration

```yaml
# ml/csrnet_config.yaml
model:
  name: "CSRNet"
  input_size: [640, 480]
  input_channels: 3
  output_channels: 1
  dilations: [1, 1, 2, 2, 4, 4]

training:
  epochs: 100
  batch_size: 1
  learning_rate: 0.0001
  weight_decay: 0.0005
  momentum: 0.95
  
  # Optimization
  optimizer: "Adam"
  scheduler: "ReduceLROnPlateau"
  
  # Regularization
  dropout: 0.5
  augmentation: true
  
  # Mixed precision
  mixed_precision: true
  accumulation_steps: 8

inference:
  batch_size: 1
  device: "cuda:0"
  half_precision: true

paths:
  dataset: "ml/datasets/shanghaitech"
  weights: "ml/checkpoints"
  logs: "ml/logs"
  tensorboard: "ml/runs"
```

### Start Training

```bash
cd ml

# Train CSRNet
python src/csrnet/training/train.py \
  --config csrnet_config.yaml \
  --epochs 100 \
  --batch-size 1 \
  --learning-rate 0.0001 \
  --dataset shanghaitech \
  --data-part A

# With mixed precision (faster)
python src/csrnet/training/train.py \
  --config csrnet_config.yaml \
  --mixed-precision \
  --accumulation-steps 8 \
  --epochs 100
```

### Monitor Training

```bash
# TensorBoard
tensorboard --logdir ml/runs

# Visit: http://localhost:6006
```

### Training Script Example

```python
# ml/src/csrnet/training/train.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.cuda.amp import autocast, GradScaler
import tensorboard

def train_csrnet(config):
    """Train CSRNet model"""
    
    # Load model
    model = CSRNet(dilations=config['model']['dilations'])
    model.to('cuda:0')
    
    # Load dataset
    train_dataset = CrowdDataset(
        config['paths']['dataset'],
        split='train'
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=True,
        num_workers=4
    )
    
    # Optimizer
    optimizer = Adam(
        model.parameters(),
        lr=config['training']['learning_rate'],
        weight_decay=config['training']['weight_decay']
    )
    
    # Loss function
    criterion = nn.MSELoss()
    
    # Mixed precision
    scaler = GradScaler() if config['training']['mixed_precision'] else None
    
    # TensorBoard
    writer = SummaryWriter(config['paths']['tensorboard'])
    
    # Training loop
    for epoch in range(config['training']['epochs']):
        total_loss = 0
        
        for batch_idx, (images, density_maps) in enumerate(train_loader):
            images = images.to('cuda:0')
            density_maps = density_maps.to('cuda:0')
            
            optimizer.zero_grad()
            
            if scaler:
                with autocast():
                    output = model(images)
                    loss = criterion(output, density_maps)
                
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                output = model(images)
                loss = criterion(output, density_maps)
                loss.backward()
                optimizer.step()
            
            total_loss += loss.item()
            
            if (batch_idx + 1) % 10 == 0:
                print(f"Epoch {epoch+1}, Batch {batch_idx+1}: Loss = {loss.item():.4f}")
        
        avg_loss = total_loss / len(train_loader)
        writer.add_scalar('Loss/train', avg_loss, epoch)
        
        # Save checkpoint
        if (epoch + 1) % 10 == 0:
            torch.save(
                model.state_dict(),
                f"{config['paths']['weights']}/csrnet_epoch_{epoch+1}.pth"
            )
        
        print(f"Epoch {epoch+1} completed. Average Loss: {avg_loss:.4f}")
    
    writer.close()
    print("Training completed!")

# Run training
if __name__ == "__main__":
    import yaml
    
    with open('csrnet_config.yaml') as f:
        config = yaml.safe_load(f)
    
    train_csrnet(config)
```

## VMamba Fine-tuning

### VMamba Fine-tuning Configuration

```yaml
# ml/config/vmamba_finetune.yaml
model:
  type: "vmamba"
  variant: "tiny"  # tiny, small, base
  pretrained: true
  num_classes: 1

training:
  epochs: 50
  batch_size: 4
  learning_rate: 0.0001
  warmup_epochs: 5
  
  # Data augmentation
  augmentation:
    random_crop: true
    horizontal_flip: true
    color_jitter: true
    
  # Regularization
  dropout: 0.1
  stochastic_depth: 0.1

optimizer:
  name: "AdamW"
  weight_decay: 0.05
  betas: [0.9, 0.999]

scheduler:
  name: "cosine"
  warmup_epochs: 5
```

### Fine-tune VMamba

```bash
# Fine-tune on ShanghaiTech
python ml/src/models/tmtb/finetune.py \
  --config ml/config/vmamba_finetune.yaml \
  --dataset shanghaitech \
  --epochs 50 \
  --batch-size 4 \
  --learning-rate 0.0001
```

## Transfer Learning

### Use Pre-trained Weights

```python
import torch

# Load pre-trained CSRNet
model = CSRNet()
pretrained_weights = torch.load('weights/csrnet_pretrained.pth')
model.load_state_dict(pretrained_weights)

# Fine-tune on new dataset
# Keep early layers frozen
for param in model.features[:8].parameters():
    param.requires_grad = False

# Train only later layers
optimizer = Adam(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=0.00001  # Lower learning rate
)
```

## Hyperparameter Tuning

### Grid Search

```python
from itertools import product
from ml.src.csrnet.training.train import train_csrnet

# Define parameter ranges
param_grid = {
    'learning_rate': [0.00001, 0.0001, 0.001],
    'batch_size': [1, 2, 4],
    'weight_decay': [0.0001, 0.0005, 0.001]
}

best_mae = float('inf')
best_params = None

for params in product(*param_grid.values()):
    config = {
        'learning_rate': params[0],
        'batch_size': params[1],
        'weight_decay': params[2]
    }
    
    print(f"Training with {config}")
    mae = train_csrnet(config)
    
    if mae < best_mae:
        best_mae = mae
        best_params = config
        print(f"New best! MAE: {mae:.2f}")

print(f"\nBest params: {best_params}")
print(f"Best MAE: {best_mae:.2f}")
```

### Random Search

```python
import random

search_space = {
    'learning_rate': [0.00001, 0.00005, 0.0001, 0.0005, 0.001],
    'batch_size': [1, 2, 4, 8],
    'dropout': [0.2, 0.3, 0.5],
    'weight_decay': [0, 0.0001, 0.0005, 0.001]
}

for trial in range(10):
    config = {
        k: random.choice(v) for k, v in search_space.items()
    }
    print(f"Trial {trial+1}: {config}")
    mae = train_csrnet(config)
    print(f"MAE: {mae:.2f}\n")
```

## Checkpointing

### Save Checkpoints

```python
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
    'config': config
}

torch.save(checkpoint, f'checkpoints/model_epoch_{epoch}.pth')
```

### Resume Training

```python
# Load checkpoint
checkpoint = torch.load('checkpoints/model_epoch_50.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
epoch = checkpoint['epoch']
```

## Model Evaluation

### Evaluate on Test Set

```python
def evaluate_model(model, test_loader):
    """Evaluate model on test set"""
    
    model.eval()
    total_mae = 0
    total_mse = 0
    
    with torch.no_grad():
        for images, density_maps in test_loader:
            images = images.to('cuda:0')
            density_maps = density_maps.to('cuda:0')
            
            output = model(images)
            
            pred_count = output.sum().item()
            true_count = density_maps.sum().item()
            
            mae = abs(pred_count - true_count)
            mse = (pred_count - true_count) ** 2
            
            total_mae += mae
            total_mse += mse
    
    avg_mae = total_mae / len(test_loader)
    avg_rmse = (total_mse / len(test_loader)) ** 0.5
    
    print(f"Test MAE: {avg_mae:.2f}")
    print(f"Test RMSE: {avg_rmse:.2f}")
    
    return {'mae': avg_mae, 'rmse': avg_rmse}
```

## Export Model

### Export to ONNX

```python
import torch.onnx

model.eval()

dummy_input = torch.randn(1, 3, 640, 480).to('cuda:0')

torch.onnx.export(
    model,
    dummy_input,
    "weights/csrnet.onnx",
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
)
```

### Export to TorchScript

```python
model.eval()
traced_model = torch.jit.trace(model, torch.randn(1, 3, 640, 480).to('cuda:0'))
traced_model.save("weights/csrnet_scripted.pt")
```

## Distributed Training

### Data Parallel (Single Machine, Multi-GPU)

```python
import torch.nn as nn

model = CSRNet()
model = nn.DataParallel(model, device_ids=[0, 1])
```

### Distributed Data Parallel (Multi-Machine)

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

dist.init_process_group("nccl")
model = CSRNet().to(rank)
model = DDP(model, device_ids=[rank])
```

## Training Tips

1. **Start with small learning rate** (0.00001)
2. **Use mixed precision** for 2-3× speedup
3. **Enable gradient accumulation** for larger effective batch size
4. **Monitor GPU memory** with `nvidia-smi`
5. **Save checkpoints** every N epochs
6. **Use validation set** to detect overfitting
7. **Augment data** to improve generalization
8. **Normalize inputs** (ImageNet stats)

## Common Issues

### Out of Memory
- Reduce batch size
- Enable mixed precision
- Reduce image size

### Slow Training
- Increase number of workers in DataLoader
- Enable persistent_workers
- Use mixed precision training
- Profile with py-spy

### Poor Accuracy
- Check data preprocessing
- Verify annotations
- Increase training epochs
- Try different architecture
- Use data augmentation

---

**Last Updated**: 2024  
**Status**: Comprehensive training guide
