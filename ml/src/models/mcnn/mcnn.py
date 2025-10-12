"""
MCNN: Multi-Column CNN for Crowd Counting
Paper: https://www.cv-foundation.org/openaccess/content_cvpr_2016/papers/Zhang_Single-Image_Crowd_Counting_CVPR_2016_paper.pdf
"""

import torch
import torch.nn as nn
import logging

logger = logging.getLogger(__name__)

class MCNN(nn.Module):
    """
    Multi-Column CNN for crowd counting
    Uses three columns with different receptive fields
    """
    
    def __init__(self):
        super(MCNN, self).__init__()
        
        # Column 1: Small receptive field (local features)
        self.column1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=9, padding=4),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(16, 32, kernel_size=7, padding=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(32, 16, kernel_size=7, padding=3),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(16, 8, kernel_size=7, padding=3),
            nn.ReLU(inplace=True)
        )
        
        # Column 2: Medium receptive field
        self.column2 = nn.Sequential(
            nn.Conv2d(3, 20, kernel_size=7, padding=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(20, 40, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(40, 20, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(20, 10, kernel_size=5, padding=2),
            nn.ReLU(inplace=True)
        )
        
        # Column 3: Large receptive field (global features)
        self.column3 = nn.Sequential(
            nn.Conv2d(3, 24, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(24, 48, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(48, 24, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(24, 12, kernel_size=3, padding=1),
            nn.ReLU(inplace=True)
        )
        
        # Fusion layer: Merge three columns
        self.fusion = nn.Sequential(
            nn.Conv2d(30, 1, kernel_size=1)  # 8 + 10 + 12 = 30
        )
        
        self._initialize_weights()
        logger.info("🏗️ MCNN architecture created")
    
    def _initialize_weights(self):
        """Initialize network weights"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.normal_(m.weight, std=0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Input tensor (B, 3, H, W)
            
        Returns:
            Density map (B, 1, H/4, W/4)
        """
        # Process through three columns
        x1 = self.column1(x)
        x2 = self.column2(x)
        x3 = self.column3(x)
        
        # Concatenate along channel dimension
        x = torch.cat([x1, x2, x3], dim=1)
        
        # Fuse features
        x = self.fusion(x)
        
        return x
    
    def predict_count(self, x):
        """
        Predict crowd count from input image
        
        Args:
            x: Input tensor (B, 3, H, W)
            
        Returns:
            Predicted count (float)
        """
        with torch.no_grad():
            density_map = self.forward(x)
            count = density_map.sum().item()
        
        return count


def load_mcnn(checkpoint_path=None, device='cuda'):
    """
    Load MCNN model with optional checkpoint
    
    Args:
        checkpoint_path: Path to model checkpoint
        device: Device to load model on
        
    Returns:
        Loaded MCNN model
    """
    logger.info("🔧 Loading MCNN model...")
    
    model = MCNN()
    
    if checkpoint_path:
        try:
            logger.info(f"📥 Loading checkpoint from {checkpoint_path}")
            checkpoint = torch.load(checkpoint_path, map_location=device)
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if 'state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['state_dict'])
                elif 'model' in checkpoint:
                    model.load_state_dict(checkpoint['model'])
                else:
                    model.load_state_dict(checkpoint)
            else:
                model.load_state_dict(checkpoint)
            
            logger.info("✅ Checkpoint loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load checkpoint: {e}")
            logger.warning("🔧 Using randomly initialized model")
    
    model = model.to(device)
    model.eval()
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"📊 Total parameters: {total_params:,}")
    
    return model


if __name__ == "__main__":
    # Test the model
    logging.basicConfig(level=logging.INFO)
    
    model = MCNN()
    print(f"Model created successfully")
    
    # Test forward pass
    x = torch.randn(1, 3, 512, 512)
    output = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Predicted count: {model.predict_count(x)}")
