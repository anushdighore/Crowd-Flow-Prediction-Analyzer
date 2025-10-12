"""
Camera API endpoints for the application.

This module provides RESTful API endpoints for camera operations including
streaming, connection testing, and frame processing.
"""

import asyncio
import logging
import time
from typing import Optional
import cv2

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

# Import camera client and services
from app.camera.camera import camera_client
from app.services.stream_manager import stream_manager
from app.camera.config import camera_config

# Configure logging
logger = logging.getLogger(__name__)

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
    """Process a single frame from the camera."""
    frame = await camera_client.get_frame(camera_url)
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not get frame from camera")

    start_time = time.time()
    
    try:
        if model_name.lower() == "csrnet" and csrnet_api:
            result = csrnet_api.predict(frame, source="webcam")
            count = result.get("count", -1)
        elif model_name.lower() == "tmtb" and tmtb_api:
            result = tmtb_api.predict(frame, source="webcam")
            count = result.get("count", -1)
        else:
            raise ValueError(f"Unsupported or unavailable model: {model_name}")

        return {
            "status": "success",
            "model": model_name,
            "count": count,
            "processing_time": round(time.time() - start_time, 3),
            "image_size": f"{frame.shape[1]}x{frame.shape[0]}",
        }
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
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