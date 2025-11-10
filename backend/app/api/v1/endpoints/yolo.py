"""YOLOv8 FastAPI Endpoint - Object Detection based Crowd Counting"""
import sys
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import logging
import base64

ml_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

from models.yolo import api as yolo_api

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/yolo", tags=["YOLO"])

@router.get("/health")
async def health():
    """Health check endpoint for YOLO model"""
    return {
        "status": "ok",
        "model": "YOLOv8",
        "description": "YOLOv8-based object detection for crowd counting",
        "approach": "Object Detection"
    }

@router.post("/count")
async def count(file: UploadFile = File(...)):
    """Count people using YOLOv8 object detection
    
    Returns:
        - count: Detected number of people
        - boxes: Bounding boxes of detected people
        - confidence: Detection confidence scores
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Run YOLO prediction with boxes
        result = yolo_api.predict(image, return_boxes=True)
        
        return {
            "status": "success",
            "count": result["rounded_count"],
            "raw_count": result["count"],
            "inference_time_ms": result["inference_time_ms"],
            "device": result["device"],
            "model": "YOLOv8",
            "approach": "Object Detection",
            "original_size": result.get("original_size"),
            "boxes": result.get("boxes", []),
            "confidence": result.get("average_confidence", 0.0)
        }
    except Exception as e:
        logger.error(f"YOLO count error: {e}")
        raise HTTPException(status_code=500, detail=f"YOLO prediction failed: {str(e)}")

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Alias for count endpoint (matches CSRNet & TMTB API)"""
    return await count(file)

@router.post("/detect")
async def detect(file: UploadFile = File(...)):
    """Detailed detection endpoint - returns boxes with visualization
    
    Returns:
        - count: Number of people detected
        - boxes: List of bounding boxes with coordinates and confidence
        - annotated_image: Base64 encoded image with boxes drawn
        - visualization: Metadata about the visualization
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Run YOLO prediction with detailed output
        result = yolo_api.predict(image, return_boxes=True, visualize=True)
        
        response = {
            "status": "success",
            "count": result["rounded_count"],
            "raw_count": result["count"],
            "inference_time_ms": result["inference_time_ms"],
            "device": result["device"],
            "model": "YOLOv8",
            "boxes": result.get("boxes", []),
            "num_boxes": len(result.get("boxes", [])),
            "average_confidence": result.get("average_confidence", 0.0),
            "min_confidence": result.get("min_confidence", 0.0),
            "max_confidence": result.get("max_confidence", 0.0)
        }
        
        # Add annotated image if available
        if "annotated_image" in result and result["annotated_image"] is not None:
            try:
                # Convert to base64
                buffered = io.BytesIO()
                Image.fromarray(result["annotated_image"]).save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                response["annotated_image"] = f"data:image/jpeg;base64,{img_base64}"
                response["visualization"] = {
                    "format": "JPEG",
                    "has_boxes": True,
                    "line_thickness": 2,
                    "font_scale": 0.5
                }
            except Exception as viz_error:
                logger.warning(f"Could not generate visualization: {viz_error}")
        
        return response
        
    except Exception as e:
        logger.error(f"YOLO detect error: {e}")
        raise HTTPException(status_code=500, detail=f"YOLO detection failed: {str(e)}")

@router.post("/webcam")
async def webcam_count(file: UploadFile = File(...)):
    """Webcam frame counting endpoint - optimized for real-time
    
    Uses lighter YOLO settings for real-time processing
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Run YOLO prediction optimized for webcam
        result = yolo_api.predict(image, source="webcam")
        
        return {
            "status": "success",
            "count": result["rounded_count"],
            "raw_count": result["count"],
            "inference_time_ms": result["inference_time_ms"],
            "device": result["device"],
            "model": "YOLOv8",
            "source": "webcam",
            "fps": 1000 / result["inference_time_ms"] if result["inference_time_ms"] > 0 else 0
        }
    except Exception as e:
        logger.error(f"YOLO webcam error: {e}")
        raise HTTPException(status_code=500, detail=f"YOLO webcam prediction failed: {str(e)}")

@router.post("/batch")
async def batch_predict(files: list = File(...)):
    """Batch prediction endpoint - process multiple images
    
    Args:
        files: List of image files
        
    Returns:
        List of predictions for each image
    """
    try:
        results = []
        
        for file in files:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            
            result = yolo_api.predict(image, return_boxes=True)
            
            results.append({
                "filename": file.filename,
                "count": result["rounded_count"],
                "raw_count": result["count"],
                "inference_time_ms": result["inference_time_ms"],
                "device": result["device"],
                "status": "success"
            })
        
        return {
            "status": "success",
            "total_images": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"YOLO batch error: {e}")
        raise HTTPException(status_code=500, detail=f"YOLO batch prediction failed: {str(e)}")

@router.get("/info")
async def info():
    """Get YOLOv8 model information"""
    return {
        "model": "YOLOv8",
        "variant": "nano (yolov8n)",
        "approach": "Object Detection",
        "class_detected": "Person (COCO class 0)",
        "input_size": "Variable (auto-resizing)",
        "output": "Bounding boxes with confidence scores",
        "features": [
            "Real-time object detection",
            "Bounding box coordinates",
            "Confidence scores per detection",
            "Annotated visualizations",
            "Batch processing",
            "GPU acceleration"
        ],
        "strengths": [
            "Returns actual bounding boxes",
            "Good for sparse to medium crowds",
            "Fast inference",
            "Direct person detection"
        ],
        "limitations": [
            "Struggles with very dense crowds",
            "May miss partially occluded people",
            "Requires clear person silhouettes"
        ],
        "comparison": {
            "vs_csrnet": "YOLO uses detection, CSRNet uses density regression. YOLO better for sparse crowds.",
            "vs_tmtb": "YOLO is detection-based, TMTB is appearance-based. TMTB better for occlusion.",
            "vs_ensemble": "Single model vs ensemble. Ensemble more robust but slower."
        }
    }
