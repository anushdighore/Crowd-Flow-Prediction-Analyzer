# backend/app/camera/camera.py

import asyncio
import logging
import time
from typing import Optional, Generator, Dict, Any

import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, Response, StreamingResponse

# Import configuration
from .config import camera_config, ml_config
from .camera_client import camera_client

# Configure logging
logger = logging.getLogger(__name__)

# Import ML processor
try:
    from app.services.ml_processor import ml_processor
    from app.services.csrnet import csrnet_api
    from app.services.tmtb import tmtb_api
except ImportError as e:
    logger.warning(f"Could not import model APIs: {e}")
    csrnet_api = tmtb_api = None

router = APIRouter()

# Initialize the camera client when the module loads
# This ensures the client is ready to use when the application starts
camera_client = camera_client  # This uses the singleton instance from camera_client.py

@router.get("/test-connection")
async def test_camera_connection(camera_url: str = camera_config.url):
    """Test connection to a camera URL and verify it returns a valid image."""
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

async def mjpeg_stream(camera_url: str, use_ml: bool = False, fps: float = 10.0) -> Generator[bytes, None, None]:
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

            if use_ml and ml_processor:
                frame = ml_processor.process_frame(frame)

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
async def video_feed(
    camera_url: str = Query(default=camera_config.default_url),
    use_ml: bool = False,
):
    """Stream video feed from camera URL with optional ML processing."""
    return StreamingResponse(
        mjpeg_stream(camera_url, use_ml),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
        },
    )

@router.get("/process")
async def process_camera_feed(
    camera_url: str = Query(default=camera_config.default_url),
    model_name: str = "csrnet",
):
    """Process a frame from the camera using the specified model."""
    frame = await camera_client.get_frame(camera_url)
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not get frame from camera")

    start_time = time.time()
    
    try:
        if model_name.lower() == "csrnet" and ml_config.models["csrnet"] and csrnet_api:
            result = csrnet_api.predict(frame, source="webcam")
            count = result.get("count", -1)
        elif model_name.lower() == "tmtb" and ml_config.models["tmtb"] and tmtb_api:
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

@router.get("/proxy")
async def proxy_camera_image(
    url: str = Query(..., description="URL of the camera image")
):
    """Proxy image from camera URL with proper caching headers."""
    try:
        frame = await camera_client.get_frame(url)
        if frame is None:
            raise HTTPException(status_code=400, detail="Could not get frame from URL")

        _, buf = cv2.imencode(".jpg", frame)
        return Response(
            content=buf.tobytes(),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))