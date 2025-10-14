"""
Crowd Counter Backend API

Main FastAPI application for crowd counting models with HLS streaming support.
"""
import asyncio
import logging
import sys
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
import cv2
import numpy as np

# Import API routers
from app.camera.camera import router as camera_router
from app.api import camera as api_camera
from app.camera.hls import router as hls_router
from app.services.hls_packager import hls_packager
from app.services.stream_manager import stream_manager
from app.api.v1.endpoints.csrnet import router as csrnet_router
from prometheus_fastapi_instrumentator import Instrumentator

# Add ml/src to path
ml_path = Path(__file__).parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

try:
    from models.csrnet import api as csrnet_api
    from models.tmtb import api as tmtb_api
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import model APIs: {e}")
    csrnet_api = tmtb_api = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crowd Counter API",
    description="Multi-model crowd counting API with CSRNet, VMamba, and HLS streaming",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.1.6:3000",
    "http://192.168.1.6:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include API routers
app.include_router(camera_router, prefix="/api", tags=["camera"])
app.include_router(hls_router, prefix="/api", tags=["hls"])
app.include_router(api_camera.router, prefix="/api", tags=["camera"])
app.include_router(csrnet_router, prefix="/api/v1", tags=["csrnet"])

# Mount static files for HLS segments
hls_static_dir = Path(__file__).parent.parent / "static" / "hls"
hls_static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/streams", StaticFiles(directory=str(hls_static_dir)), name="streams")

# Add Prometheus metrics
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Start background tasks
    asyncio.create_task(cleanup_task())
    asyncio.create_task(stream_manager.cleanup_inactive_streams())
    logger.info("🚀 Application startup complete")

async def cleanup_task():
    """Background task to clean up old HLS segments"""
    while True:
        try:
            hls_packager.cleanup_old_segments()
            await asyncio.sleep(60)  # Run every minute
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
            await asyncio.sleep(60)

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Crowd Counter API",
        "version": "1.0.0",
        "models": ["CSRNet", "TMTB (VMamba)"],
        "features": ["REST API", "WebSocket", "HLS Streaming"],
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Crowd Counter API",
        "active_streams": len([s for s in hls_packager.sessions.values() if s.active])
    }

@app.websocket("/ws/count")
async def websocket_count(websocket: WebSocket):
    """WebSocket endpoint for real-time webcam counting"""
    await websocket.accept()
    logger.info("✅ WebSocket connected for real-time counting")
    
    frame_number = 0
    
    try:
        while True:
            data = await websocket.receive_json()
            frame_data = data.get("frame") or data.get("image")
            model_type = data.get("model", "csrnet")
            
            if not frame_data:
                await websocket.send_json({
                    "success": False,
                    "error": "No frame data received"
                })
                continue
            
            import base64
            if frame_data.startswith("data:image"):
                frame_data = frame_data.split(",")[1]
            
            image_bytes = base64.b64decode(frame_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Run prediction based on selected model
            try:
                if model_type.lower() == "tmtb" and tmtb_api:
                    result = tmtb_api.predict(image, source="webcam")
                    model_name = "TMTB"
                else:
                    result = csrnet_api.predict(image, source="webcam") if csrnet_api else {"count": 0, "inference_time_ms": 0}
                    model_name = "CSRNet"
                
                frame_number += 1
                
                await websocket.send_json({
                    "success": True,
                    "model": model_name.lower(),
                    "count": result.get("count", result.get("rounded_count", 0)),
                    "inference_time_ms": result.get("inference_time_ms", 0),
                    "frame_number": frame_number,
                    "fps": 1000 / result["inference_time_ms"] if result.get("inference_time_ms", 0) > 0 else 0
                })
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                await websocket.send_json({
                    "success": False,
                    "error": f"Prediction failed: {str(e)}"
                })
                
    except WebSocketDisconnect:
        logger.info("❌ WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "success": False,
                "error": str(e)
            })
        except:
            pass

@app.websocket("/ws/external-camera")
async def websocket_external_camera(websocket: WebSocket):
    """WebSocket endpoint for external IP camera with real-time ML predictions"""
    await websocket.accept()
    logger.info("✅ WebSocket connected for external camera")
    
    from app.camera.camera import camera_client
    
    frame_number = 0
    camera_url = None
    model_type = "csrnet"
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle control messages
            if "camera_url" in data:
                camera_url = data["camera_url"]
                model_type = data.get("model", "csrnet")
                logger.info(f"📹 External camera URL set: {camera_url}, Model: {model_type}")
                await websocket.send_json({
                    "success": True,
                    "message": "Camera URL configured",
                    "camera_url": camera_url
                })
                continue
            
            # Request for next frame
            if data.get("action") == "get_frame":
                if not camera_url:
                    await websocket.send_json({
                        "success": False,
                        "error": "Camera URL not set. Send camera_url first."
                    })
                    continue
                
                try:
                    # Get frame from external camera
                    frame = await camera_client.get_frame(camera_url)
                    
                    if frame is None:
                        await websocket.send_json({
                            "success": False,
                            "error": "Failed to get frame from camera"
                        })
                        continue
                    
                    # Convert to PIL Image
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Run ML prediction
                    if model_type.lower() == "tmtb" and tmtb_api:
                        result = tmtb_api.predict(pil_image, source="surveillance")
                        model_name = "TMTB"
                    else:
                        result = csrnet_api.predict(pil_image, source="surveillance") if csrnet_api else {"count": 0, "inference_time_ms": 0, "rounded_count": 0}
                        model_name = "CSRNet"
                    
                    frame_number += 1
                    
                    # Encode frame as JPEG for sending back
                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    import base64
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    await websocket.send_json({
                        "success": True,
                        "model": model_name.lower(),
                        "count": result.get("rounded_count", result.get("count", 0)),
                        "raw_count": result.get("count", 0),
                        "inference_time_ms": result.get("inference_time_ms", 0),
                        "device": result.get("device", "unknown"),
                        "frame_number": frame_number,
                        "fps": 1000 / result["inference_time_ms"] if result.get("inference_time_ms", 0) > 0 else 0,
                        "frame": f"data:image/jpeg;base64,{frame_base64}"
                    })
                    
                except Exception as e:
                    logger.error(f"Frame processing error: {e}", exc_info=True)
                    await websocket.send_json({
                        "success": False,
                        "error": f"Frame processing failed: {str(e)}"
                    })
                
    except WebSocketDisconnect:
        logger.info("❌ External camera WebSocket disconnected")
    except Exception as e:
        logger.error(f"External camera WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "success": False,
                "error": str(e)
            })
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )