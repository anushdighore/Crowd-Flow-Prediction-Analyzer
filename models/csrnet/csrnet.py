import torch.nn as nn
import torch
from torchvision import models
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class CSRNet(nn.Module):
    def __init__(self, load_weights=False):
        super(CSRNet, self).__init__()
        self.seen = 0
        self.frontend_feat = [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512]
        self.backend_feat  = [512, 512, 512,256,128,64]
        self.frontend = make_layers(self.frontend_feat)
        self.backend = make_layers(self.backend_feat,in_channels = 512,dilation = True)
        self.output_layer = nn.Conv2d(64, 1, kernel_size=1)
        if not load_weights:
            mod = models.vgg16(pretrained = True)
            self._initialize_weights()
            # Python 3 fix: use range instead of xrange, use list()
            frontend_items = list(self.frontend.state_dict().items())
            vgg_items = list(mod.state_dict().items())
            for i in range(len(frontend_items)):
                frontend_items[i][1].data[:] = vgg_items[i][1].data[:]
    def forward(self,x):
        x = self.frontend(x)
        x = self.backend(x)
        x = self.output_layer(x)
        return x
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.normal_(m.weight, std=0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            
                
def make_layers(cfg, in_channels = 3,batch_norm=False,dilation = False):
    if dilation:
        d_rate = 2
    else:
        d_rate = 1
    layers = []
    for v in cfg:
        if v == 'M':
            layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
        else:
            conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=d_rate,dilation = d_rate)
            if batch_norm:
                layers += [conv2d, nn.BatchNorm2d(v), nn.ReLU(inplace=True)]
            else:
                layers += [conv2d, nn.ReLU(inplace=True)]
            in_channels = v
    return nn.Sequential(*layers)


def load_csrnet(checkpoint_path, device='cpu'):
    """
    Load CSRNet model from checkpoint with proper error handling
    
    Args:
        checkpoint_path: Path to .pth checkpoint file
        device: 'cpu' or 'cuda'
    
    Returns:
        model: Loaded CSRNet model in eval mode
    """
    logger.info(f"Loading CSRNet from {checkpoint_path}")
    
    # Initialize model
    model = CSRNet(load_weights=True)
    
    # Load checkpoint
    try:
        checkpoint = torch.load(checkpoint_path, map_location=device)
        logger.info(f"Checkpoint type: {type(checkpoint)}")
        
        # Handle different checkpoint formats
        if isinstance(checkpoint, dict):
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
                logger.info("Found 'state_dict' key in checkpoint")
            elif 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
                logger.info("Found 'model_state_dict' key in checkpoint")
            else:
                state_dict = checkpoint
                logger.info("Using checkpoint dict directly")
        else:
            state_dict = checkpoint
            logger.info("Checkpoint is direct state dict")
        
        # Remove 'module.' prefix if present (from DataParallel)
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k.replace('module.', '') if k.startswith('module.') else k
            new_state_dict[name] = v
        
        model.load_state_dict(new_state_dict)
        logger.info("Successfully loaded model weights")
        
    except Exception as e:
        logger.error(f"Error loading checkpoint: {e}")
        raise
    
    model.to(device)
    model.eval()
    
    return model