"""
Camera API endpoints for the application.

This module provides RESTful API endpoints for camera operations including
streaming, connection testing, and frame processing.
"""

import asyncio
import io
import logging
import sys
import time
import os
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
from PIL import Image

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

# Import camera client and services
from app.camera.camera import camera_client
from app.services.stream_manager import stream_manager
from app.camera.config import camera_config

# Configure logging
logger = logging.getLogger(__name__)

# Add ml/src to path for model imports

# Get the absolute path to the ml/src directory
current_dir = os.path.dirname(__file__)
backend_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(backend_dir)
ml_src_path = os.path.join(project_root, "ml", "src")

if ml_src_path not in sys.path:
    sys.path.insert(0, ml_src_path)
    logger.info(f"Added ML path: {ml_src_path}")

# Also add the models directory directly
models_path = os.path.join(ml_src_path, "models")
if models_path not in sys.path:
    sys.path.insert(0, models_path)
    logger.info(f"Added models path: {models_path}")

logger.info(f"Current Python path includes: {[p for p in sys.path if 'ml' in p or 'models' in p]}")

try:
    logger.info("Importing model APIs...")
    from models.csrnet import api as csrnet_api
    logger.info("✓ Successfully imported CSRNet API")
    from models.tmtb import api as tmtb_api
    logger.info("✓ Successfully imported TMTB API")
except ImportError as e:
    logger.error(f"❌ Could not import model APIs: {e}", exc_info=True)
    csrnet_api = tmtb_api = None

# Create API router
router = APIRouter(prefix="/camera", tags=["camera"])

@router.get("/test-connection")
async def test_camera_connection(camera_url: str = camera_config.default_url):
    """Test connection to a camera URL."""
    start_time = time.time()
    
    try:
        frame = await camera_client.get_frame(camera_url)
        if frame is None:
            raise HTTPException(status_code=400, detail="Failed to get frame from camera")
            
        h, w = frame.shape[:2]
        return {
            "status": "success",
            "message": "Connected and received valid image",
            "camera_url": camera_url,
            "response_time_seconds": round(time.time() - start_time, 3),
            "image_dimensions": f"{w}x{h}",
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": f"Failed to connect to camera: {str(e)}",
                "camera_url": camera_url,
                "response_time_seconds": round(time.time() - start_time, 3),
            }
        )

async def mjpeg_stream(camera_url: str, fps: float = 10.0):
    """Generate MJPEG stream from camera URL."""
    boundary = b"--frame"
    interval = max(0.01, 1.0 / fps)
    
    while True:
        try:
            frame = await camera_client.get_frame(camera_url)
            if frame is None:
                logger.warning("Got empty frame, retrying...")
                await asyncio.sleep(1)
                continue

            _, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            jpg = buf.tobytes()
            headers = (
                boundary + b"\r\n" +
                f"Content-Type: image/jpeg\r\nContent-Length: {len(jpg)}\r\n\r\n".encode()
            )
            yield headers + jpg + b"\r\n"
            await asyncio.sleep(interval)
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            await asyncio.sleep(1)

@router.get("/stream")
async def stream_camera(camera_url: str = Query(default=camera_config.default_url)):
    """Stream video from a camera URL."""
    return StreamingResponse(
        mjpeg_stream(camera_url),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
        },
    )

@router.get("/process")
async def process_frame(
    camera_url: str = Query(default=camera_config.default_url),
    model_name: str = "csrnet"
):
    """Process a single frame from the camera with ML prediction."""
    try:
        # Get frame from camera
        frame = await camera_client.get_frame(camera_url)
        if frame is None:
            raise HTTPException(status_code=400, detail="Could not get frame from camera")

        # Convert frame to PIL Image for model processing
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        # Run ML prediction
        if model_name.lower() == "csrnet" and csrnet_api:
            result = csrnet_api.predict(pil_image, source="surveillance")
            return {
                "status": "success",
                "model": "csrnet",
                "count": result.get("rounded_count", 0),
                "raw_count": result.get("count", 0),
                "inference_time_ms": result.get("inference_time_ms", 0),
                "device": result.get("device", "unknown"),
                "image_size": f"{frame.shape[1]}x{frame.shape[0]}",
            }
        elif model_name.lower() == "tmtb" and tmtb_api:
            result = tmtb_api.predict(pil_image, source="surveillance")
            return {
                "status": "success",
                "model": "tmtb",
                "count": result.get("rounded_count", 0),
                "raw_count": result.get("count", 0),
                "inference_time_ms": result.get("inference_time_ms", 0),
                "device": result.get("device", "unknown"),
                "image_size": f"{frame.shape[1]}x{frame.shape[0]}",
            }
        else:
            raise HTTPException(
                status_code=503,
                detail=f"Model '{model_name}' is not available. CSRNet available: {csrnet_api is not None}, TMTB available: {tmtb_api is not None}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing frame: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_camera_status():
    """Get the status of camera services."""
    try:
        return {
            "status": "operational",
            "active_streams": len(stream_manager.get_active_streams()) if hasattr(stream_manager, 'get_active_streams') else 0,
            "uptime": time.time() - (stream_manager.start_time if hasattr(stream_manager, 'start_time') else time.time()),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": "Service unavailable"
            }
        )