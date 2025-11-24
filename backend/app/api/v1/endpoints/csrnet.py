"""CSRNet FastAPI Endpoint"""
import sys
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from PIL import Image
import io
import logging
import base64
import cv2
import numpy as np

ml_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

from models.csrnet import api as csrnet_api

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/csrnet", tags=["CSRNet"])

@router.get("/health")
async def health():
    return {"status": "ok", "model": "CSRNet"}

@router.post("/count")
async def count(file: UploadFile = File(...)):
    """Count endpoint - config-driven sizing for uploads"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Get heatmap if requested (from query param or form field)
        return_heatmap = False  # Default: don't return heatmap
        
        result = csrnet_api.predict(image, source="image", return_density_map=return_heatmap)
        
        response_data = {
            "status": "success",
            "count": result["rounded_count"],
            "raw_count": result["count"],
            "inference_time_ms": result["inference_time_ms"],
            "device": result["device"],
            "original_size": result.get("original_size"),
            "processed_size": result.get("processed_size")
        }
        
        # Generate heatmap if density map is available
        if return_heatmap and "density_map" in result:
            try:
                heatmap_overlay = csrnet_api.generate_heatmap(result["density_map"], image)
                _, buffer = cv2.imencode('.jpg', heatmap_overlay)
                img_base64 = base64.b64encode(buffer).decode()
                response_data["heatmap"] = f"data:image/jpeg;base64,{img_base64}"
                logger.info("✅ Heatmap generated successfully")
            except Exception as heatmap_err:
                logger.warning(f"⚠️ Heatmap generation failed: {heatmap_err}")
        
        return response_data
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Alias for count endpoint"""
    return await count(file)

@router.post("/webcam")
async def webcam_count(file: UploadFile = File(...)):
    """Webcam frame count endpoint - config-driven sizing for real-time"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        result = csrnet_api.predict(image, source="webcam")  # Uses config for webcam sizing
        return {
            "status": "success",
            "count": result["rounded_count"],
            "raw_count": result["count"],
            "inference_time_ms": result["inference_time_ms"],
            "device": result["device"]
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
