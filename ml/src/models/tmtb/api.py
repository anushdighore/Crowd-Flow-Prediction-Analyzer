"""TMTB (VMamba) API - Lazy loading with optimization"""
import torch
import time
from pathlib import Path
from PIL import Image
from typing import Dict, Union
import logging

# Import config loader with fallback for different import contexts
try:
    from ...core.config_loader import load_tmtb_config
except (ImportError, ValueError):
    from core.config_loader import load_tmtb_config

logger = logging.getLogger(__name__)

_model_cache = {}
_preprocessor = None


def get_preprocessor():
    """Get or create preprocessor (lazy initialization)"""
    global _preprocessor
    if _preprocessor is None:
        import torchvision.transforms as transforms
        _preprocessor = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        logger.info("✅ TMTB preprocessor initialized")
    return _preprocessor


def get_model(checkpoint_path: str = None):
    """Get cached model or load new one (lazy loading with optimized CPU-first strategy)"""
    global _model_cache
    
    # Default checkpoint path
    if checkpoint_path is None:
        checkpoint_path = str(Path(__file__).parent.parent.parent.parent / "fine-tunned-models" / "tmtb_jhu_corrected.pth")
    
    # Return cached model if available
    if checkpoint_path in _model_cache:
        logger.debug(f"✅ Using cached TMTB model")
        return _model_cache[checkpoint_path]
    
    # Load model with optimized CPU-first strategy (from notebook optimization)
    logger.info(f"📦 Loading TMTB model from: {checkpoint_path}")
    start_time = time.time()
    
    try:
        # Import model class
        from .model import mamba
        
        # Get device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"   Using device: {device}")
        
        # CRITICAL: Create model on CPU first (avoids 15+ minute GPU initialization overhead)
        with torch.no_grad():
            # Save original default device
            original_default = None
            if hasattr(torch, 'get_default_device'):
                original_default = torch.get_default_device()
            
            # Force CPU for model creation
            torch.set_default_device('cpu')
            
            # Create model structure on CPU (fast: ~0.7s)
            model = mamba(25, vmamba_pretrained_path=None)
            
            # Load checkpoint weights
            checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
            
            # Load weights into model
            missing_keys, unexpected_keys = model.load_state_dict(checkpoint, strict=False)
            
            # Move to target device
            model = model.to(device)
            model.eval()
            
            # Restore original default device
            if original_default is not None and device.type == 'cuda':
                torch.set_default_device('cuda')
        
        load_time = time.time() - start_time
        total_params = sum(p.numel() for p in model.parameters())
        
        logger.info(f"✅ TMTB model loaded in {load_time:.2f}s")
        logger.info(f"   Parameters: {total_params:,}")
        logger.info(f"   Device: {next(model.parameters()).device}")
        
        if missing_keys:
            logger.debug(f"   Missing keys: {len(missing_keys)} (OK for fine-tuned models)")
        if unexpected_keys:
            logger.debug(f"   Unexpected keys: {len(unexpected_keys)} (OK)")
        
        # Cache the model
        _model_cache[checkpoint_path] = model
        
        return model
        
    except Exception as e:
        logger.error(f"❌ Failed to load TMTB model: {e}")
        raise


def predict(image: Union[str, Path, Image.Image], checkpoint_path: str = None, source: str = "image") -> Dict:
    """Run TMTB prediction with config-driven resizing
    
    Args:
        image: Input image (path or PIL Image)
        checkpoint_path: Path to checkpoint (default: ml/fine-tunned-models/tmtb_jhu_corrected.pth)
        source: Input source type - 'image'/'upload', 'webcam', 'video', 'surveillance'
                Determines resize dimensions from config file
    
    Returns:
        Dict with count, inference_time_ms, device, etc.
    """
    start_time = time.time()
    
    # Load config to get dimensions for this source
    config = load_tmtb_config()
    dims = config.preprocessing.get_dimensions(source)
    max_dimension = max(dims.length, dims.breadth)
    
    try:
        # Load image if path provided
        if isinstance(image, (str, Path)):
            image = Image.open(image).convert('RGB')
        elif not isinstance(image, Image.Image):
            raise ValueError(f"Invalid image type: {type(image)}")
        
        original_size = image.size
        
        # Smart resizing for performance (same strategy as CSRNet)
        if max(original_size) > max_dimension:
            ratio = max_dimension / max(original_size)
            new_size = tuple(int(dim * ratio) for dim in original_size)
            image = image.resize(new_size, Image.BILINEAR)
            resized = True
            processed_size = new_size
            logger.debug(f"Resized {original_size} → {new_size} for speed (source: {source})")
        else:
            resized = False
            processed_size = original_size
        
        # Get model and preprocessor (lazy loading)
        model = get_model(checkpoint_path)
        preprocessor = get_preprocessor()
        
        # Get device
        device = next(model.parameters()).device
        
        # Preprocess image
        img_tensor = preprocessor(image).unsqueeze(0).to(device)
        
        # Run inference
        inference_start = time.time()
        with torch.no_grad():
            output = model(img_tensor)
            
            # TMTB returns (density_map, cls_score) tuple
            if isinstance(output, tuple):
                density_map = output[0]
            else:
                density_map = output
            
            # Calculate count
            count = density_map.sum().item()
        
        inference_time = (time.time() - inference_start) * 1000  # Convert to ms
        total_time = (time.time() - start_time) * 1000
        
        # Prepare result
        result = {
            "count": count,
            "rounded_count": int(round(count)),
            "inference_time_ms": round(inference_time, 2),
            "total_time_ms": round(total_time, 2),
            "device": str(device),
            "original_size": original_size,
            "processed_size": processed_size,
            "resized": resized,
            "model": "TMTB (VMamba)",
            "parameters": sum(p.numel() for p in model.parameters()),
            "source": source,
            "config_dimensions": {"length": dims.length, "breadth": dims.breadth}
        }
        
        logger.debug(f"TMTB prediction: {result['rounded_count']} people in {inference_time:.2f}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ TMTB prediction failed: {e}")
        raise


def clear_cache():
    """Clear model cache to free memory"""
    global _model_cache
    count = len(_model_cache)
    _model_cache.clear()
    logger.info(f"🧹 Cleared {count} cached TMTB model(s)")
    
    # Clear GPU cache if available
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.info("🧹 Cleared GPU cache")
