"""
CSRNet: Fixed Implementation with Proper Weight Loading
This version handles multiple checkpoint formats and ensures correct loading
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
    """
    CSRNet for crowd counting
    Architecture matches the original paper exactly
    """
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
        
        # Initialize weights with VGG16 for frontend
        if not load_weights:
            self._initialize_weights()
        
        logger.info("🏗️  CSRNet architecture created")
    
    def forward(self, x):
        """Forward pass"""
        x = self.frontend(x)
        x = self.backend(x)
        x = self.output_layer(x)
        return x
    
    def _initialize_weights(self):
        """Initialize weights with VGG16 pretrained on ImageNet"""
        logger.info("🔧 Initializing frontend with VGG16 pretrained weights...")
        
        # Load VGG16
        vgg = models.vgg16(pretrained=True)
        
        # Copy frontend weights from VGG16
        frontend_dict = self.frontend.state_dict()
        vgg_dict = vgg.features.state_dict()
        
        # Map VGG layers to frontend
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
        
        logger.info("✅ Weights initialized")


def load_csrnet(checkpoint_path, device='cpu'):
    """
    Load CSRNet model with pretrained weights
    Handles multiple checkpoint formats
    
    Args:
        checkpoint_path: Path to .pth checkpoint file
        device: Device to load model on ('cpu' or 'cuda')
    
    Returns:
        Loaded CSRNet model in eval mode
    """
    logger.info("=" * 60)
    logger.info("🔧 Loading CSRNet Model")
    logger.info("=" * 60)
    
    # Create model
    model = CSRNet(load_weights=True)  # Don't initialize with VGG16
    
    # Load checkpoint
    logger.info(f"📥 Loading checkpoint from: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    logger.info("✅ Checkpoint file loaded")
    
    # Extract state dict
    if isinstance(checkpoint, dict):
        logger.info(f"📊 Checkpoint keys: {list(checkpoint.keys())}")
        
        if 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
            logger.info("   Using 'state_dict' key")
        elif 'model' in checkpoint:
            state_dict = checkpoint['model']
            logger.info("   Using 'model' key")
        else:
            state_dict = checkpoint
            logger.info("   Using checkpoint directly as state_dict")
    else:
        state_dict = checkpoint
        logger.info("   Checkpoint is OrderedDict/dict, using directly")
    
    # Handle 'module.' prefix (from DataParallel)
    if any(k.startswith('module.') for k in state_dict.keys()):
        logger.info("🔧 Removing 'module.' prefix from keys...")
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:] if k.startswith('module.') else k  # remove 'module.'
            new_state_dict[name] = v
        state_dict = new_state_dict
    
    # Check if architecture matches
    model_keys = set(model.state_dict().keys())
    checkpoint_keys = set(state_dict.keys())
    
    missing_keys = model_keys - checkpoint_keys
    unexpected_keys = checkpoint_keys - model_keys
    
    if missing_keys:
        logger.warning(f"⚠️  Missing keys in checkpoint: {len(missing_keys)}")
        logger.warning(f"   First 5: {list(missing_keys)[:5]}")
    
    if unexpected_keys:
        logger.warning(f"⚠️  Unexpected keys in checkpoint: {len(unexpected_keys)}")
        logger.warning(f"   First 5: {list(unexpected_keys)[:5]}")
    
    # Load state dict with strict=False to handle partial matches
    try:
        model.load_state_dict(state_dict, strict=False)
        logger.info("✅ Model weights loaded successfully")
    except Exception as e:
        logger.error(f"❌ Error loading state dict: {e}")
        logger.info("🔧 Attempting flexible loading...")
        
        # Try loading layer by layer
        model_dict = model.state_dict()
        loaded_count = 0
        for k, v in state_dict.items():
            if k in model_dict and model_dict[k].shape == v.shape:
                model_dict[k] = v
                loaded_count += 1
        
        model.load_state_dict(model_dict)
        logger.info(f"✅ Loaded {loaded_count}/{len(model_dict)} parameters")
    
    # Move to device and set eval mode
    model = model.to(device)
    model.eval()
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    logger.info(f"📊 Model Statistics:")
    logger.info(f"   Total parameters: {total_params:,}")
    logger.info(f"   Trainable parameters: {trainable_params:,}")
    logger.info(f"   Device: {device}")
    logger.info("=" * 60)
    
    return model


def test_model_inference(model, device='cpu'):
    """
    Test model with dummy input
    
    Args:
        model: CSRNet model
        device: Device to run test on
    
    Returns:
        True if test passes
    """
    logger.info("🧪 Testing model inference...")
    
    try:
        # Create dummy input (3x256x256 RGB image)
        dummy_input = torch.randn(1, 3, 256, 256).to(device)
        
        with torch.no_grad():
            output = model(dummy_input)
        
        logger.info(f"   Input shape: {dummy_input.shape}")
        logger.info(f"   Output shape: {output.shape}")
        logger.info(f"   Output range: [{output.min().item():.4f}, {output.max().item():.4f}]")
        logger.info(f"   Predicted count: {output.sum().item():.2f}")
        
        # Check for valid output
        if torch.isnan(output).any():
            logger.error("❌ Output contains NaN values!")
            return False
        
        if torch.isinf(output).any():
            logger.error("❌ Output contains Inf values!")
            return False
        
        logger.info("✅ Model test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test the model
    logging.basicConfig(level=logging.INFO)
    
    # Create model
    model = CSRNet()
    print(f"\nModel created with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Test forward pass
    test_model_inference(model)
