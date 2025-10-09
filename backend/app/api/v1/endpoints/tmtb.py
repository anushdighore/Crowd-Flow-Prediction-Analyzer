"""TMTB (VMamba) FastAPI Endpoint - Optimized with Lazy Loading"""
import sys
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import logging

ml_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

from models.tmtb import api as tmtb_api

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tmtb", tags=["TMTB"])

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "model": "TMTB (VMamba)",
        "description": "State-of-the-art VMamba-based crowd counting"
    }

@router.post("/count")
async def count(file: UploadFile = File(...)):
    """Count endpoint - config-driven sizing for uploads"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        result = tmtb_api.predict(image, source="image")  # Uses config for upload sizing
        return {
            "status": "success",
            "count": result["rounded_count"],
            "raw_count": result["count"],
            "inference_time_ms": result["inference_time_ms"],
            "device": result["device"],
            "original_size": result.get("original_size"),
            "processed_size": result.get("processed_size"),
            "model": "TMTB"
        }
    except Exception as e:
        logger.error(f"TMTB count error: {e}")
        raise HTTPException(status_code=500, detail=f"TMTB prediction failed: {str(e)}")

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Alias for count endpoint (matches CSRNet API)"""
    return await count(file)

@router.post("/webcam")
async def webcam_count(file: UploadFile = File(...)):
    """Webcam frame count endpoint - config-driven sizing for real-time"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        result = tmtb_api.predict(image, source="webcam")  # Uses config for webcam sizing
        return {
            "status": "success",
            "count": result["rounded_count"],
            "raw_count": result["count"],
            "inference_time_ms": result["inference_time_ms"],
            "device": result["device"],
            "model": "TMTB"
        }
    except Exception as e:
        logger.error(f"TMTB webcam error: {e}")
        raise HTTPException(status_code=500, detail=f"TMTB prediction failed: {str(e)}")

