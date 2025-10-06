from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.vmamba_official import load_tmtb_model
from utils.preprocess import preprocess_frame
from utils.postprocess import get_count_from_density
import cv2
import numpy as np
import torch 
import time
import logging
from typing import Dict, Any
import os
# from utils.visualize import generate_heatmap_overlay

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TMTB Crowd Counter API",
    description="VMamba-TMTB based crowd counting API for real-time inference",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global model and device variables
model = None
device = None

@app.on_event("startup")
async def startup_event():
    """Load model on application startup"""
    global model, device

    checkpoint_path = "./checkpoints/jhu_5.pth"

    if not os.path.exists(checkpoint_path):
        logger.error(f"❌ Checkpoint file not found: {checkpoint_path}")
        return

    try:
        # Initialize device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"🔧 Using device: {device}")

        # Load model
        map_location = str(device)
        model = load_tmtb_model(checkpoint_path, device=map_location)
        model.eval()
        model.to(device)

        logger.info("✅ VMamba-TMTB model loaded successfully")

        # Log model parameters count
        total_params = sum(p.numel() for p in model.parameters())
        logger.info(f"📊 Model parameters: {total_params:,}")

    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        model = None

@app.get("/")
async def root() -> Dict[str, str]:
    """Health check endpoint"""
    status = "Model loaded" if model is not None else "Model not loaded"
    return {
        "message": "TMTB Crowd Counter API",
        "status": status,
        "device": str(device) if device else "Unknown"
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Detailed health check"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "device": str(device) if device else "Unknown",
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available()
    }

@app.post("/count")
async def count_crowd(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Count crowd in uploaded image using VMamba-TMTB model

    Args:
        file: Uploaded image file (JPEG/PNG)

    Returns:
        JSON response with crowd count and processing time
    """
    # Check if model is loaded
    if model is None:
        logger.error("Model not available for inference")
        raise HTTPException(
            status_code=500, 
            detail="Model not loaded. Check server logs for initialization errors."
        )

    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only image files are accepted."
        )

    try:
        # Read and validate image bytes
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        logger.info(f"📸 Processing image: {file.filename} ({len(contents)} bytes)")

        # Decode image using OpenCV
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image format. Supported formats: JPEG, PNG, BMP, TIFF"
            )

        logger.info(f"🖼️ Image decoded: {img.shape} (H, W, C)")

        # Preprocess image for model input
        start_preprocess = time.time()
        input_tensor = preprocess_frame(img, max_long_edge=1280)

        # Move to device
        input_tensor = input_tensor.to(device)
        preprocess_time = (time.time() - start_preprocess) * 1000

        logger.info(f"⚙️ Preprocessing completed: {input_tensor.shape} tensor")

        # Run model inference
        start_inference = time.time()
        with torch.no_grad():
            outputs = model(input_tensor)
        inference_time = (time.time() - start_inference) * 1000

        if isinstance(outputs, (tuple, list)):
            density_map = outputs[0]
            cls_scores = outputs[1] if len(outputs) > 1 else None
        else:
            density_map = outputs
            cls_scores = None

        if isinstance(density_map, (tuple, list)):
            density_map = density_map[0]

        logger.info(f"🧠 Inference completed: {tuple(density_map.shape)} density map")

        # Convert density map to crowd count
        start_postprocess = time.time()
        density_tensor = density_map
        if density_tensor.ndim == 4:
            density_tensor = density_tensor.squeeze(0).squeeze(0)
        elif density_tensor.ndim == 3:
            density_tensor = density_tensor.squeeze(0)
        density_np = density_tensor.detach().cpu().numpy()
        crowd_count = get_count_from_density(density_np)
        postprocess_time = (time.time() - start_postprocess) * 1000

        total_processing_time = preprocess_time + inference_time + postprocess_time

        # Prepare response
        response: Dict[str, Any] = {
            "crowd_count": int(round(crowd_count)),
            "processing_time_ms": round(total_processing_time, 2),
            "timing_breakdown": {
                "preprocess_ms": round(preprocess_time, 2),
                "inference_ms": round(inference_time, 2),
                "postprocess_ms": round(postprocess_time, 2)
            },
            "image_info": {
                "filename": file.filename,
                "size_bytes": len(contents),
                "dimensions": f"{img.shape[1]}x{img.shape[0]}"  # W x H
            }
        }

        if cls_scores is not None:
            response["classification_logits"] = (
                cls_scores.squeeze().detach().cpu().tolist()
                if isinstance(cls_scores, torch.Tensor)
                else cls_scores
            )

        logger.info(f"✅ Count completed: {crowd_count} people detected in {total_processing_time:.2f}ms")

        return response

    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he

    except Exception as e:
        # Log unexpected errors
        logger.error(f"💥 Unexpected error during inference: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return HTTPException(
        status_code=500,
        detail="Internal server error occurred"
    )
if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Starting TMTB Crowd Counter API server...")

    # Run with uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True  # Enable auto-reload for development
    )
