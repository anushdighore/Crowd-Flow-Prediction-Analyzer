"""
TMTB (VMamba) Crowd Counting API Endpoint

This endpoint uses the TMTB model for crowd counting inference.
Pure PyTorch implementation - no CUDA extensions required.
"""

import sys
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import logging
import torch
import torchvision.transforms as transforms

# Add ML package to path
ml_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

# Import from ML package
from models.tmtb.vmamba_official import load_tmtb_model

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/tmtb", tags=["TMTB"])

# Global model and device
model = None
device = None
transform = None


def initialize_tmtb():
    """Initialize TMTB model"""
    global model, device, transform
    
    if model is not None:
        logger.info("TMTB already initialized")
        return
    
    logger.info("=" * 60)
    logger.info("🚀 Initializing TMTB (VMamba) Model")
    logger.info("=" * 60)
    
    # Detect device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"🖥️  Device: {device}")
    logger.info(f"💡 Using PyTorch-only implementation (no CUDA extensions)")
    
    # Checkpoint path
    checkpoint_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "checkpoints" / "jhu_5.pth"
    
    if not checkpoint_path.exists():
        logger.error(f"❌ Checkpoint not found: {checkpoint_path}")
        raise FileNotFoundError(f"TMTB checkpoint not found at {checkpoint_path}")
    
    logger.info(f"📥 Loading from: {checkpoint_path}")
    
    try:
        # Load model
        model = load_tmtb_model(str(checkpoint_path), device=str(device))
        model.eval()
        
        # Initialize transform
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        logger.info("✅ TMTB initialized successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize TMTB: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    initialize_tmtb()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for TMTB service
    
    Returns:
        dict: Service status
    """
    return {
        "status": "healthy" if model is not None else "not_initialized",
        "model": "TMTB (VMamba)",
        "model_loaded": model is not None,
        "device": str(device) if device is not None else "unknown",
        "device_type": "GPU" if torch.cuda.is_available() else "CPU",
        "implementation": "PyTorch-only (no CUDA extensions)"
    }


@router.post("/count")
async def count_crowd(file: UploadFile = File(...)):
    """
    Count people in uploaded image using TMTB
    
    Args:
        file: Uploaded image file
        
    Returns:
        dict: Crowd count and metadata
    """
    # Initialize model if not already done
    if model is None:
        initialize_tmtb()
    
    logger.info("=" * 60)
    logger.info(f"📸 Processing: {file.filename}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be an image.")
    
    try:
        # Read image bytes
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        orig_size = image.size
        
        logger.info(f"📐 Image size: {orig_size[0]}x{orig_size[1]}")
        
    except Exception as e:
        logger.error(f"❌ Error loading image: {e}")
        raise HTTPException(status_code=400, detail=f"Could not read image: {str(e)}")
    
    try:
        # Preprocess
        logger.info("🔧 Preprocessing...")
        image_tensor = transform(image).unsqueeze(0).to(device)
        
        logger.info(f"   Tensor shape: {list(image_tensor.shape)}")
        logger.info(f"   Tensor range: [{image_tensor.min():.3f}, {image_tensor.max():.3f}]")
        
    except Exception as e:
        logger.error(f"❌ Preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {str(e)}")
    
    try:
        # Run inference
        logger.info("🤖 Running inference...")
        with torch.no_grad():
            output = model(image_tensor)
        
        # Handle output format
        if isinstance(output, tuple):
            density_map = output[0]
        else:
            density_map = output
        
        # Calculate count
        count = density_map.sum().item()
        
        logger.info(f"   Output shape: {list(density_map.shape)}")
        logger.info(f"👥 Predicted count: {count:.2f}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")
    
    return {
        "count": round(count, 2),
        "model": "TMTB (VMamba)",
        "image_size": {
            "width": orig_size[0],
            "height": orig_size[1]
        },
        "density_map_size": {
            "width": density_map.shape[3],
            "height": density_map.shape[2]
        },
        "device": str(device),
        "implementation": "PyTorch-only"
    }


@router.get("/info")
async def model_info():
    """
    Get TMTB model information
    
    Returns:
        dict: Model metadata
    """
    if model is None:
        initialize_tmtb()
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        "model": "TMTB (VMamba)",
        "architecture": "Vision Mamba with TMTB modifications",
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "checkpoint": "jhu_5.pth",
        "implementation": "PyTorch-only (no CUDA extensions)",
        "performance_note": "~2-5x slower than CUDA version but fully compatible"
    }
