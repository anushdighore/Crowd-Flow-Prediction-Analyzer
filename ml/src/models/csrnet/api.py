"""CSRNet API - Direct connection matching notebook pattern"""
import torch
import time
from pathlib import Path
from PIL import Image
from typing import Dict, Union
import logging

from .csrnet import load_csrnet

# Import config loader with fallback for different import contexts
try:
    from ...core.config_loader import load_csrnet_config
except (ImportError, ValueError):
    from core.config_loader import load_csrnet_config

logger = logging.getLogger(__name__)

_model_cache = {}
_preprocessor = None


def get_preprocessor():
    """Get or create preprocessor"""
    global _preprocessor
    if _preprocessor is None:
        try:
            from ...preprocessing.csrnet_preprocess import CSRNetPreprocessor
            _preprocessor = CSRNetPreprocessor()
        except ImportError:
            import torchvision.transforms as transforms
            _preprocessor = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
    return _preprocessor


def get_model(checkpoint_path: str = None):
    """Get cached model or load new one"""
    global _model_cache
    if checkpoint_path is None:
        checkpoint_path = str(Path(__file__).parent.parent.parent.parent / "checkpoints" / "csrnet.pth")
    if checkpoint_path in _model_cache:
        return _model_cache[checkpoint_path]
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = load_csrnet(checkpoint_path, device=str(device))
    _model_cache[checkpoint_path] = model
    return model


def predict(image: Union[str, Path, Image.Image], checkpoint_path: str = None, source: str = "image") -> Dict:
    """Run CSRNet prediction with config-driven resizing
    
    Args:
        image: Input image (path or PIL Image)
        checkpoint_path: Path to model checkpoint
        source: Input source type - 'image'/'upload', 'webcam', 'video', 'surveillance'
                Determines resize dimensions from config file
    """
    start_time = time.time()
    
    # Load config to get dimensions for this source
    config = load_csrnet_config()
    dims = config.preprocessing.get_dimensions(source)
    max_dimension = max(dims.length, dims.breadth)
    
    # Load and convert image
    if isinstance(image, (str, Path)):
        img = Image.open(image).convert('RGB')
    else:
        img = image.convert('RGB')
    
    original_size = img.size
    
    # Smart resize: maintain aspect ratio, limit max dimension
    w, h = img.size
    if max(w, h) > max_dimension:
        scale = max_dimension / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        # Make dimensions divisible by 8 (CSRNet requirement)
        new_w = (new_w // 8) * 8
        new_h = (new_h // 8) * 8
        img = img.resize((new_w, new_h), Image.BILINEAR)
        logger.info(f"Resized {original_size} -> {img.size} for faster inference (source: {source})")
    
    # Get model and preprocessor
    model = get_model(checkpoint_path)
    preprocessor = get_preprocessor()
    device = next(model.parameters()).device
    
    # Preprocess image
    if hasattr(preprocessor, 'preprocess'):
        img_tensor = preprocessor.preprocess(img)
    else:
        img_tensor = preprocessor(img).unsqueeze(0)
    
    img_tensor = img_tensor.to(device)
    
    # Run inference
    with torch.no_grad():
        density_map = model(img_tensor)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        count = density_map.sum().item()
    
    inference_time = (time.time() - start_time) * 1000
    
    return {
        "count": float(count),
        "rounded_count": int(round(count)),
        "inference_time_ms": float(inference_time),
        "device": str(device),
        "density_map_shape": tuple(density_map.shape),
        "original_size": original_size,
        "processed_size": img.size,
        "source": source,
        "config_dimensions": {"length": dims.length, "breadth": dims.breadth}
    }
