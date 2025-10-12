"""
CSRNet - Complete Working Implementation
"""
import torch
import torch.nn as nn
from torchvision import models
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

def make_layers(cfg, in_channels=3, batch_norm=False, dilation=False):
    """Create layers from config"""
    if dilation:
        d_rate = 2
    else:
        d_rate = 1
    
    layers = []
    for v in cfg:
        if v == 'M':
            layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
        else:
            conv2d = nn.Conv2d(in_channels, v, kernel_size=3, 
                             padding=d_rate, dilation=d_rate)
            if batch_norm:
                layers += [conv2d, nn.BatchNorm2d(v), nn.ReLU(inplace=True)]
            else:
                layers += [conv2d, nn.ReLU(inplace=True)]
            in_channels = v
    return nn.Sequential(*layers)


class CSRNet(nn.Module):
    """CSRNet for crowd counting"""
    def __init__(self, load_weights=False):
        super(CSRNet, self).__init__()
        
        self.seen = 0
        
        # Architecture definition from original paper
        self.frontend_feat = [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512]
        self.backend_feat = [512, 512, 512, 256, 128, 64]
        
        # Build layers
        self.frontend = make_layers(self.frontend_feat)
        self.backend = make_layers(self.backend_feat, in_channels=512, dilation=True)
        self.output_layer = nn.Conv2d(64, 1, kernel_size=1)
        
        if not load_weights:
            self._initialize_weights()
        
        logger.info("🏗️  CSRNet architecture created")
    
    def forward(self, x):
        """Forward pass - returns density map"""
        x = self.frontend(x)
        x = self.backend(x)
        x = self.output_layer(x)
        # Apply ReLU to ensure non-negative values
        x = torch.nn.functional.relu(x)
        return x
    
    def _initialize_weights(self):
        """Initialize weights with VGG16"""
        logger.info("🔧 Initializing with VGG16...")
        vgg = models.vgg16(pretrained=True)
        
        # Copy frontend weights
        frontend_dict = self.frontend.state_dict()
        vgg_dict = vgg.features.state_dict()
        
        vgg_keys = list(vgg_dict.keys())
        frontend_keys = list(frontend_dict.keys())
        
        for i in range(min(len(vgg_keys), len(frontend_keys))):
            if frontend_dict[frontend_keys[i]].shape == vgg_dict[vgg_keys[i]].shape:
                frontend_dict[frontend_keys[i]] = vgg_dict[vgg_keys[i]]
        
        self.frontend.load_state_dict(frontend_dict)
        
        # Initialize backend and output
        for m in self.backend.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.normal_(m.weight, std=0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
        
        nn.init.normal_(self.output_layer.weight, std=0.01)
        if self.output_layer.bias is not None:
            nn.init.constant_(self.output_layer.bias, 0)


def load_csrnet(checkpoint_path, device='cpu'):
    """
    Load CSRNet model with pretrained weights
    
    Args:
        checkpoint_path: Path to checkpoint .pth file
        device: 'cpu' or 'cuda'
    
    Returns:
        Loaded model in eval mode
    """
    logger.info("="*60)
    logger.info("🔧 Loading CSRNet Model")
    logger.info("="*60)
    
    # Create model
    model = CSRNet(load_weights=True)
    
    # Load checkpoint
    logger.info(f"📥 Loading: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Extract state_dict
    if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
        state_dict = checkpoint['state_dict']
        logger.info(f"✅ Loaded checkpoint from epoch {checkpoint.get('epoch', 'unknown')}")
        logger.info(f"   Best MAE: {checkpoint.get('best_prec1', 'N/A')}")
    else:
        state_dict = checkpoint
        logger.info("✅ Loaded state dict directly")
    
    # Handle 'module.' prefix if present
    if any(k.startswith('module.') for k in state_dict.keys()):
        logger.info("🔧 Removing 'module.' prefix...")
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:] if k.startswith('module.') else k
            new_state_dict[name] = v
        state_dict = new_state_dict
    
    # Load weights
    model.load_state_dict(state_dict)
    logger.info("✅ Weights loaded successfully")
    
    # Move to device and set eval mode
    model = model.to(device)
    model.eval()
    
    # Disable gradients
    for param in model.parameters():
        param.requires_grad = False
    
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"📊 Total parameters: {total_params:,}")
    logger.info(f"🖥️  Device: {device}")
    logger.info("="*60)
    
    return model


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    model = load_csrnet("./checkpoint/csrnet.pth")
    print("\n✅ Model loaded successfully!")
