"""CSRNet FastAPI Endpoint"""
import sys
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import logging

ml_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

from models.csrnet import api as csrnet_api

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/csrnet", tags=["CSRNet"])

@router.get("/health")
async def health():
    return {"status": "ok", "model": "CSRNet"}

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        result = csrnet_api.predict(image)
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
