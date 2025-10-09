"""CSRNet API Endpoint - Using direct api.py connection"""
import sys
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import logging

# Add ML package to path
ml_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

# Import from new minimal API
from models.csrnet import api as csrnet_api

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/csrnet", tags=["CSRNet"])
    logger.info(f"🖥️  Device: {device}")
    
    # Checkpoint path (relative to backend root)
    checkpoint_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "checkpoints" / "csrnet.pth"
    
    if not checkpoint_path.exists():
        logger.error(f"❌ Checkpoint not found: {checkpoint_path}")
        raise FileNotFoundError(f"CSRNet checkpoint not found at {checkpoint_path}")
    
    logger.info(f"📥 Loading from: {checkpoint_path}")
    
    try:
        # Load model
        model = load_csrnet(str(checkpoint_path), device=str(device))
        
        # Initialize processors
        preprocessor = CSRNetPreprocessor()
        postprocessor = CSRNetPostprocessor()
        
        logger.info("✅ CSRNet initialized successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize CSRNet: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    initialize_csrnet()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for CSRNet service
    
    Returns:
        dict: Service status
    """
    return {
        "status": "healthy" if model is not None else "not_initialized",
        "model": "CSRNet",
        "model_loaded": model is not None,
        "device": str(device) if device is not None else "unknown",
        "device_type": "GPU" if torch.cuda.is_available() else "CPU"
    }


@router.post("/count")
async def count_crowd(file: UploadFile = File(...)):
    """
    Count people in uploaded image using CSRNet
    
    Args:
        file: Uploaded image file
        
    Returns:
        dict: Crowd count and metadata
    """
    # Initialize model if not already done
    if model is None:
        initialize_csrnet()
    
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
        image_tensor = preprocessor.preprocess(image)
        image_tensor = image_tensor.to(device)
        
        logger.info(f"   Tensor shape: {list(image_tensor.shape)}")
        logger.info(f"   Tensor range: [{image_tensor.min():.3f}, {image_tensor.max():.3f}]")
        
    except Exception as e:
        logger.error(f"❌ Preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {str(e)}")
    
    try:
        # Inference
        logger.info("🧠 Running inference...")
        
        with torch.no_grad():
            model.eval()
            density_map = model(image_tensor)
        
        logger.info(f"   Density map shape: {list(density_map.shape)}")
        logger.info(f"   Density range: [{density_map.min().item():.4f}, {density_map.max().item():.4f}]")
        
        # Postprocess
        logger.info("🔧 Postprocessing...")
        crowd_count = postprocessor.density_to_count(density_map)
        stats = postprocessor.get_statistics(density_map)
        
        logger.info(f"✅ Final count: {crowd_count}")
        logger.info("=" * 60)
        
        return {
            "success": True,
            "model": "CSRNet",
            "count": crowd_count,
            "statistics": stats,
            "image_size": f"{orig_size[0]}x{orig_size[1]}",
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")


@router.post("/count-with-heatmap")
async def count_with_heatmap(file: UploadFile = File(...)):
    """
    Count people and generate heatmap visualization
    
    Args:
        file: Uploaded image file
        
    Returns:
        dict: Crowd count, statistics, and base64 heatmap
    """
    # Initialize model if not already done
    if model is None:
        initialize_csrnet()
    
    logger.info("=" * 60)
    logger.info(f"📸 Processing with heatmap: {file.filename}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be an image.")
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        orig_size = image.size
        
        # Preprocess
        image_tensor = preprocessor.preprocess(image)
        image_tensor = image_tensor.to(device)
        
        # Inference
        with torch.no_grad():
            model.eval()
            density_map = model(image_tensor)
        
        # Postprocess with heatmap
        result = postprocessor.process_output(
            density_map, 
            original_image=image,
            include_heatmap=True
        )
        
        # Convert heatmap to base64
        import base64
        buffered = io.BytesIO()
        result['heatmap'].save(buffered, format="PNG")
        heatmap_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        logger.info(f"✅ Count: {result['count']} | Heatmap generated")
        logger.info("=" * 60)
        
        return {
            "success": True,
            "model": "CSRNet",
            "count": result['count'],
            "statistics": result['statistics'],
            "heatmap": heatmap_base64,
            "image_size": f"{orig_size[0]}x{orig_size[1]}",
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
