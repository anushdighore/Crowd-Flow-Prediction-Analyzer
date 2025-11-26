"""
Crowd Counter Backend API

Main FastAPI application for crowd counting models with HLS streaming support.
"""
import asyncio
import logging
import sys
import base64
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
import cv2
import numpy as np

# Import occupancy monitoring system
ml_src_path = Path(__file__).parent.parent.parent / "ml" / "src" / "v4Updates"
sys.path.insert(0, str(ml_src_path))
from occupancy_monitor import OccupancyMonitor
from occupancy_config import OccupancyConfig
from occupancy_processor import OccupancyProcessor

# Import API routers
from app.camera.camera import router as camera_router
from app.api import camera as api_camera
from app.camera.hls import router as hls_router
from app.services.hls_packager import hls_packager
from app.services.stream_manager import stream_manager
from app.api.v1.endpoints.csrnet import router as csrnet_router
from app.api.v1.endpoints.tmtb import router as tmtb_router
from app.api.v1.endpoints.yolo import router as yolo_router
from app.api.v1.endpoints.pedestrian_tracking import router as pedestrian_tracking_router
from prometheus_fastapi_instrumentator import Instrumentator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add ml/src to path
ml_path = Path(__file__).parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

try:
    from models.csrnet import api as csrnet_api
    from models.tmtb import api as tmtb_api
    from models.yolo import api as yolo_api
    from models.unified_counter import UnifiedCounter
    from app.services.gated_model_router import get_router
    model_router = get_router()
    logger.info(f"✅ Available models: {model_router.get_available_models()}")
except ImportError as e:
    logger.warning(f"Could not import model APIs: {e}")
    csrnet_api = tmtb_api = yolo_api = None
    UnifiedCounter = None
    model_router = None

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
app.include_router(tmtb_router, prefix="/api/v1", tags=["tmtb"])
app.include_router(yolo_router, prefix="/api/v1", tags=["yolo"])
app.include_router(pedestrian_tracking_router, prefix="/api/v1", tags=["pedestrian-tracking"])

# Mount static files for HLS segments
hls_static_dir = Path(__file__).parent.parent / "static" / "hls"
hls_static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/streams", StaticFiles(directory=str(hls_static_dir)), name="streams")

# Add Prometheus metrics
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Initialize tracking counters for YOLO (lazy initialization) - SEPARATE instances for each source
webcam_tracking_counter = None
external_camera_tracking_counter = None
video_tracking_counter = None

# Import pedestrian tracker for WebSocket
try:
    from app.services.pedestrian_tracker import PedestrianTracker
    logger.info("✅ Imported PedestrianTracker service")
except ImportError as e:
    logger.warning(f"⚠️ Could not import pedestrian tracker: {e}")
    PedestrianTracker = None

def get_tracking_counter(checkpoint: str = "yolov8n.pt", source: str = "webcam"):
    """Get or create tracking counter instance for specific source
    
    Args:
        checkpoint: YOLO model checkpoint path
        source: 'webcam', 'external', or 'video' - each gets its own tracker to prevent cross-contamination
    """
    global webcam_tracking_counter, external_camera_tracking_counter, video_tracking_counter
    
    if source == "external":
        if external_camera_tracking_counter is None and UnifiedCounter is not None:
            try:
                external_camera_tracking_counter = UnifiedCounter(
                    model_type='yolo',
                    model_path=checkpoint,
                    enable_tracking=True,
                    conf_threshold=0.5,
                    iou_threshold=0.5
                )
                logger.info(f"✅ Initialized EXTERNAL CAMERA tracking counter with {checkpoint}")
            except Exception as e:
                logger.error(f"Failed to initialize external camera tracking counter: {e}")
                external_camera_tracking_counter = None
        return external_camera_tracking_counter
    elif source == "video":
        if video_tracking_counter is None and UnifiedCounter is not None:
            try:
                video_tracking_counter = UnifiedCounter(
                    model_type='yolo',
                    model_path=checkpoint,
                    enable_tracking=True,
                    conf_threshold=0.5,
                    iou_threshold=0.5
                )
                logger.info(f"✅ Initialized VIDEO tracking counter with {checkpoint}")
            except Exception as e:
                logger.error(f"Failed to initialize video tracking counter: {e}")
                video_tracking_counter = None
        return video_tracking_counter
    else:
        # Default: webcam
        if webcam_tracking_counter is None and UnifiedCounter is not None:
            try:
                webcam_tracking_counter = UnifiedCounter(
                    model_type='yolo',
                    model_path=checkpoint,
                    enable_tracking=True,
                    conf_threshold=0.5,
                    iou_threshold=0.5
                )
                logger.info(f"✅ Initialized WEBCAM tracking counter with {checkpoint}")
            except Exception as e:
                logger.error(f"Failed to initialize webcam tracking counter: {e}")
                webcam_tracking_counter = None
        return webcam_tracking_counter

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Initialize occupancy monitoring system
    global occupancy_processor
    occupancy_processor = OccupancyProcessor()
    logger.info("🚀 Occupancy monitoring system initialized")
    
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
            enable_tracking = data.get("tracking", False)
            return_heatmap = data.get("heatmap", False)
            
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
                model_name = "CSRNet"
                result = {}
                
                # Map model variants to checkpoint paths
                yolo_model_map = {
                    "yolo": "yolov8n.pt",
                    "yolo-nano": "yolov8n.pt",
                    "yolo-small": "yolov8s.pt",
                    "yolo-medium": "yolov8m.pt",
                    "yolo-large": "yolov8l.pt",
                    "yolo-xlarge": "yolov8x.pt"
                }
                
                if model_type.lower() in yolo_model_map and yolo_api:
                    # YOLO models - object detection
                    checkpoint = yolo_model_map[model_type.lower()]
                    
                    # Use UnifiedCounter with tracking if enabled
                    if enable_tracking and UnifiedCounter is not None:
                        try:
                            # Get or create tracking counter for WEBCAM
                            counter = get_tracking_counter(checkpoint, source="webcam")
                            if counter is not None:
                                # Convert PIL image to numpy
                                img_array = np.array(image)
                                if img_array.shape[-1] == 3:  # RGB
                                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                                
                                # Get prediction with tracking - ALWAYS get visualization when tracking
                                result = counter.predict(
                                    img_array,
                                    return_details=True,
                                    return_visualization=True  # Always get annotated frame with tracking
                                )
                                model_name = f"YOLO-{checkpoint.replace('.pt', '').replace('yolov8', '').upper()}-Tracking"
                            else:
                                # Fallback to regular YOLO
                                result = yolo_api.predict(
                                    image, 
                                    checkpoint_path=checkpoint,
                                    source="webcam",
                                    return_boxes=True,
                                    visualize=return_heatmap
                                )
                                model_name = f"YOLO-{checkpoint.replace('.pt', '').replace('yolov8', '').upper()}"
                        except Exception as e:
                            logger.error(f"Tracking error, falling back to regular YOLO: {e}")
                            result = yolo_api.predict(
                                image, 
                                checkpoint_path=checkpoint,
                                source="webcam",
                                return_boxes=True,
                                visualize=return_heatmap
                            )
                            model_name = f"YOLO-{checkpoint.replace('.pt', '').replace('yolov8', '').upper()}"
                    else:
                        # Regular YOLO without tracking
                        result = yolo_api.predict(
                            image, 
                            checkpoint_path=checkpoint,
                            source="webcam",
                            return_boxes=True,
                            visualize=return_heatmap
                        )
                        model_name = f"YOLO-{checkpoint.replace('.pt', '').replace('yolov8', '').upper()}"
                    
                elif model_type.lower() == "tmtb" and tmtb_api:
                    # TMTB/VMamba - density estimation
                    result = tmtb_api.predict(
                        image,
                        source="webcam",
                        return_density_map=return_heatmap
                    )
                    model_name = "TMTB"
                    
                else:
                    # CSRNet - density estimation (default)
                    result = csrnet_api.predict(image, source="webcam", return_density_map=return_heatmap) if csrnet_api else {"count": 0, "inference_time_ms": 0}
                    model_name = "CSRNet"
                    logger.info(f"🔍 CSRNet result keys: {list(result.keys())}")
                    logger.info(f"🔍 return_heatmap={return_heatmap}, has_density_map={'density_map' in result}")
                
                frame_number += 1
                
                response = {
                    "success": True,
                    "model": model_name.lower(),
                    "count": result.get("count", result.get("rounded_count", 0)),
                    "inference_time_ms": result.get("inference_time_ms", 0),
                    "frame_number": frame_number,
                    "fps": 1000 / result["inference_time_ms"] if result.get("inference_time_ms", 0) > 0 else 0
                }
                
                # Add YOLO-specific data
                if model_type.lower() in yolo_model_map:
                    response["boxes"] = result.get("boxes", [])
                    response["num_detections"] = len(result.get("boxes", []))
                    
                    if result.get("boxes"):
                        confidences = [box.get("confidence", 0) for box in result.get("boxes", [])]
                        if confidences:
                            response["average_confidence"] = sum(confidences) / len(confidences)

                    if return_heatmap and "annotated_image" in result:
                        annotated_bgr = result["annotated_image"]
                        _, buffer = cv2.imencode('.jpg', annotated_bgr)
                        img_base64 = base64.b64encode(buffer).decode()
                        response["heatmap"] = f"data:image/jpeg;base64,{img_base64}"

                # Unified heatmap generation for density maps (CSRNet/TMTB)
                if return_heatmap and model_type.lower() not in yolo_model_map:
                    heatmap_overlay = None
                    try:
                        if model_router is not None:
                            heatmap_overlay = model_router.generate_heatmap(
                                model_type,
                                result,
                                image
                            )
                        elif "density_map" in result and csrnet_api is not None:
                            heatmap_overlay = csrnet_api.generate_heatmap(
                                result["density_map"],
                                image
                            )

                        if heatmap_overlay is not None:
                            _, buffer = cv2.imencode('.jpg', heatmap_overlay)
                            img_base64 = base64.b64encode(buffer).decode()
                            response["heatmap"] = f"data:image/jpeg;base64,{img_base64}"
                    except Exception as heatmap_err:
                        logger.error(
                            f"❌ Heatmap generation failed: {heatmap_err}",
                            exc_info=True
                        )
                
                # Add enhanced occupancy data using OccupancyProcessor
                try:
                    # Generate stream ID for webcam
                    stream_id = f"webcam_{frame_number}"
                    
                    # Process ML result with enhanced occupancy features
                    enriched_result = occupancy_processor.process_ml_result(stream_id, result)
                    
                    # Extract enhanced occupancy data
                    occupancy_data = enriched_result.get("occupancy", {})
                    
                    # Add enhanced occupancy fields to WebSocket response
                    response.update({
                        "occupancy": occupancy_data,
                        "occupancy_alerts": occupancy_data.get("alerts", []),
                        "density_heatmap": occupancy_data.get("density_heatmap"),
                        "occupancy_statistics": occupancy_data.get("statistics", {}),
                        "historical_data_available": occupancy_data.get("historical_count", 0) > 0,
                        "occupancy_timestamp": occupancy_data.get("timestamp"),
                        "occupancy_stream_id": stream_id
                    })
                    
                    # Log occupancy alerts if any
                    alerts = occupancy_data.get("alerts", [])
                    if alerts:
                        for alert in alerts:
                            logger.info(f"🚨 Occupancy Alert [{alert.get('level', 'unknown').upper()}]: {alert.get('message', 'No message')}")
                        
                except Exception as occ_err:
                    logger.error(f"Error processing enhanced occupancy data: {occ_err}")
                
                # Add tracking data if enabled (for YOLO with tracking)
                if enable_tracking and model_type.lower() in yolo_model_map:
                    # Tracking data would come from unified_counter integration
                    response["unique_count"] = result.get("unique_count", response["count"])
                    tracks = result.get("tracks", [])
                    response["tracks"] = tracks
                    logger.info(f"🚶 Tracks in result: {len(tracks)} tracks")
                    if tracks:
                        for t in tracks[:2]:  # Log first 2 tracks
                            logger.info(f"  Track {t.get('id')}: trajectory has {len(t.get('trajectory', []))} points")
                    
                    if "speed_stats" in result:
                        response["speed_stats"] = result["speed_stats"]
                    
                    # TODO: Re-enable advanced metrics when pedpy WalkableArea dependency is fixed
                    # Currently disabled due to: cannot import name 'WalkableArea' from 'pedpy'
                    # if counter is not None:
                    #     try:
                    #         img_array = np.array(image)
                    #         if img_array.shape[-1] == 3:  # RGB
                    #             img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    #         frame_shape = (img_array.shape[0], img_array.shape[1])  # (height, width)
                    #         
                    #         advanced_metrics = counter.get_advanced_metrics(
                    #             frame_shape=frame_shape,
                    #             frame_rate=30,  # Assume 30fps for webcam
                    #             frame_step=25
                    #         )
                    #         
                    #         if advanced_metrics:
                    #             response["advanced_metrics"] = advanced_metrics
                    #             logger.info(f"📊 Advanced metrics: {advanced_metrics}")
                    #     except Exception as adv_err:
                    #         logger.warning(f"Advanced metrics error: {adv_err}")
                
                await websocket.send_json(response)
                
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

# Test connection endpoint for external camera
@app.get("/api/camera/test-connection")
async def test_camera_connection(camera_url: str):
    """Test if an external camera URL is reachable"""
    import httpx
    import time
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(camera_url, timeout=5.0)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Camera is reachable",
                    "response_time_seconds": round(elapsed, 3),
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "message": f"Camera returned status {response.status_code}",
                    "response_time_seconds": round(elapsed, 3)
                }
    except httpx.TimeoutException:
        return {"success": False, "message": "Connection timeout - camera not responding"}
    except httpx.ConnectError:
        return {"success": False, "message": "Cannot connect to camera - check URL and network"}
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}

@app.websocket("/ws/external-camera")
async def websocket_external_camera(websocket: WebSocket):
    """WebSocket endpoint for external IP camera with real-time ML predictions"""
    await websocket.accept()
    logger.info("✅ WebSocket connected for external camera")
    
    from app.camera.camera import camera_client
    
    frame_number = 0
    camera_url = None
    model_type = "csrnet"
    enable_tracking = False
    demo_mode = False
    demo_video_cap = None
    
    # Demo video path
    DEMO_VIDEO_PATH = Path(__file__).parent.parent.parent / "data" / "videos" / "Demo.mp4"
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle occupancy configuration updates
            if data.get("action") == "update_occupancy_config":
                try:
                    # Use consistent stream_id for all external camera streams
                    stream_id = "external_stream"
                    
                    config_updates = {
                        "max_capacity": data.get("max_capacity", 100),
                        "alert_threshold": data.get("alert_threshold", 80),
                        "reset_threshold": data.get("reset_threshold", 78),
                        "window_size_seconds": data.get("window_size", 3)
                    }
                    
                    # Update occupancy processor with new config
                    success = occupancy_processor.update_stream_config(stream_id, config_updates)
                    
                    if success:
                        logger.info(f"✅ Occupancy config updated for stream {stream_id}: {config_updates}")
                        await websocket.send_json({
                            "success": True,
                            "message": "Occupancy configuration updated",
                            "config": config_updates
                        })
                    else:
                        logger.warning(f"⚠️ Failed to update occupancy config for stream {stream_id}")
                        await websocket.send_json({
                            "success": False,
                            "message": "Failed to update occupancy configuration"
                        })
                except Exception as config_err:
                    logger.error(f"Error updating occupancy config: {config_err}")
                    await websocket.send_json({
                        "success": False,
                        "message": f"Config update error: {str(config_err)}"
                    })
                continue
            
            # Handle control messages
            if "camera_url" in data:
                camera_url = data["camera_url"]
                model_type = data.get("model", "csrnet")
                enable_tracking = data.get("tracking", False)
                demo_mode = data.get("demo_mode", False) or camera_url.startswith("demo://")
                
                # If demo mode, initialize video capture
                if demo_mode:
                    if demo_video_cap is not None:
                        demo_video_cap.release()
                    if DEMO_VIDEO_PATH.exists():
                        demo_video_cap = cv2.VideoCapture(str(DEMO_VIDEO_PATH))
                        logger.info(f"📹 Demo mode enabled with video: {DEMO_VIDEO_PATH}")
                    else:
                        logger.warning(f"⚠️ Demo video not found at {DEMO_VIDEO_PATH}")
                        demo_mode = False
                
                logger.info(f"📹 External camera URL set: {camera_url}, Model: {model_type}, Tracking: {enable_tracking}, Demo: {demo_mode}")
                
                # Handle initial occupancy configuration if provided with connection
                if "occupancy_config" in data:
                    occ_config = data["occupancy_config"]
                    stream_id = "external_stream"
                    config_updates = {
                        "max_capacity": occ_config.get("max_capacity", 100),
                        "alert_threshold": occ_config.get("alert_threshold", 80),
                        "reset_threshold": occ_config.get("reset_threshold", 78),
                        "window_size_seconds": occ_config.get("window_size", 3)
                    }
                    success = occupancy_processor.update_stream_config(stream_id, config_updates)
                    if success:
                        logger.info(f"✅ Initial occupancy config applied: {config_updates}")
                    else:
                        logger.warning(f"⚠️ Failed to apply initial occupancy config")
                
                await websocket.send_json({
                    "success": True,
                    "message": "Camera URL configured" + (" (Demo Mode)" if demo_mode else ""),
                    "camera_url": camera_url,
                    "demo_mode": demo_mode
                })
                continue
            
            # Request for next frame
            if data.get("action") == "get_frame":
                if not camera_url and not demo_mode:
                    await websocket.send_json({
                        "success": False,
                        "error": "Camera URL not set. Send camera_url first."
                    })
                    continue
                
                try:
                    # Get frame from demo video or external camera
                    if demo_mode and demo_video_cap is not None:
                        ret, frame = demo_video_cap.read()
                        if not ret:
                            # Loop the video
                            demo_video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            ret, frame = demo_video_cap.read()
                        if not ret:
                            frame = None
                    else:
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
                    
                    # Map YOLO variants
                    yolo_model_map = {
                        "yolo": "yolov8n.pt",
                        "yolo-nano": "yolov8n.pt",
                        "yolo-small": "yolov8s.pt",
                        "yolo-medium": "yolov8m.pt",
                        "yolo-large": "yolov8l.pt",
                        "yolo-xlarge": "yolov8x.pt"
                    }
                    
                    # Use UnifiedCounter with tracking if enabled and YOLO model
                    if enable_tracking and model_type.lower() in yolo_model_map and UnifiedCounter is not None:
                        try:
                            checkpoint = yolo_model_map[model_type.lower()]
                            counter = get_tracking_counter(checkpoint, source="external")
                            if counter is not None:
                                # Convert PIL to numpy BGR
                                img_array = np.array(pil_image)
                                if img_array.shape[-1] == 3:  # RGB
                                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                                
                                # Get prediction with tracking
                                result = counter.predict(
                                    img_array,
                                    return_details=True,
                                    return_visualization=True
                                )
                                model_name = f"YOLO-{checkpoint.replace('.pt', '').replace('yolov8', '').upper()}-Tracking"
                                
                                # Use annotated image as heatmap for YOLO
                                if 'annotated_image' in result:
                                    heatmap_frame = result['annotated_image']
                                else:
                                    heatmap_frame = None
                            else:
                                # Fallback to model router
                                enable_tracking = False
                                raise Exception("Tracking counter not available")
                        except Exception as track_err:
                            logger.error(f"Tracking error, falling back: {track_err}")
                            enable_tracking = False
                            # Fall through to model router
                    
                    # Run ML prediction using Gated Router (if tracking not used)
                    if not enable_tracking or model_type.lower() not in yolo_model_map:
                        if model_router:
                            # Use gated architecture for model selection
                            logger.info(f"🔀 Routing external camera to {model_type.upper()} model")
                            result = model_router.predict(
                                pil_image,
                                model_type=model_type,
                                source="surveillance",
                                return_density_map=True,
                                return_boxes=(model_type.lower() in yolo_model_map)
                            )
                            model_name = result.get('model_name', model_type.upper())
                            
                            # Generate heatmap using router (only if boxes exist for YOLO)
                            heatmap_frame = None
                            try:
                                if model_type.lower() in yolo_model_map:
                                    # Check if boxes exist before generating heatmap
                                    if result.get('boxes') and len(result['boxes']) > 0:
                                        logger.info(f"📦 Generating YOLO heatmap with {len(result['boxes'])} boxes")
                                        heatmap_frame = model_router.generate_heatmap(
                                            model_type,
                                            result,
                                            pil_image
                                        )
                                    else:
                                        logger.warning("⚠️ No boxes detected, skipping heatmap generation")
                                else:
                                    # CSRNet/TMTB heatmap
                                    heatmap_frame = model_router.generate_heatmap(
                                        model_type,
                                        result,
                                        pil_image
                                    )
                            except Exception as heatmap_error:
                                logger.error(f"Heatmap generation error: {heatmap_error}", exc_info=True)
                                heatmap_frame = None
                        else:
                            # Fallback to legacy mode
                            if model_type.lower() == "tmtb" and tmtb_api:
                                result = tmtb_api.predict(pil_image, source="surveillance", return_density_map=True)
                                model_name = "TMTB"
                                heatmap_frame = None
                            else:
                                result = csrnet_api.predict(pil_image, source="surveillance", return_density_map=True) if csrnet_api else {"count": 0, "inference_time_ms": 0, "rounded_count": 0}
                                model_name = "CSRNet"
                                heatmap_frame = None
                    
                    frame_number += 1
                    
                    # Encode original frame as JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    import base64
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Encode heatmap frame if available
                    heatmap_base64 = None
                    if heatmap_frame is not None:
                        _, heatmap_buffer = cv2.imencode('.jpg', heatmap_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                        heatmap_base64 = base64.b64encode(heatmap_buffer).decode('utf-8')
                    
                    response_data = {
                        "success": True,
                        "model": model_name.lower(),
                        "count": result.get("rounded_count", result.get("count", 0)),
                        "raw_count": result.get("count", 0),
                        "inference_time_ms": result.get("inference_time_ms", 0),
                        "device": result.get("device", "unknown"),
                        "frame_number": frame_number,
                        "fps": 1000 / result["inference_time_ms"] if result.get("inference_time_ms", 0) > 0 else 0
                    }
                    
                    # Add frame to response
                    response_data["frame"] = f"data:image/jpeg;base64,{frame_base64}"
                    
                    # Add heatmap if available
                    if heatmap_base64:
                        response_data["heatmap"] = f"data:image/jpeg;base64,{heatmap_base64}"
                    
                    # Add tracking data if enabled
                    if enable_tracking and model_type.lower() in yolo_model_map:
                        response_data["tracks"] = result.get("tracks", [])
                        response_data["unique_count"] = result.get("unique_count", response_data["count"])
                        if "annotated_image" in result:
                            _, ann_buffer = cv2.imencode('.jpg', result["annotated_image"], [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                            ann_base64 = base64.b64encode(ann_buffer).decode('utf-8')
                            response_data["annotated_frame"] = f"data:image/jpeg;base64,{ann_base64}"
                    
                    # Add enhanced occupancy data using OccupancyProcessor
                    try:
                        # Use consistent stream ID for all external camera streams
                        stream_id = "external_stream"
                        
                        # Process ML result with enhanced occupancy features
                        enriched_result = occupancy_processor.process_ml_result(stream_id, result)
                        
                        # Extract enhanced occupancy data
                        occupancy_data = enriched_result.get("occupancy", {})
                        
                        # Add enhanced occupancy fields to WebSocket response
                        response_data.update({
                            "occupancy": occupancy_data,
                            "occupancy_alerts": occupancy_data.get("alerts", []),
                            "density_heatmap": occupancy_data.get("density_heatmap"),
                            "occupancy_statistics": occupancy_data.get("statistics", {}),
                            "historical_data_available": occupancy_data.get("historical_count", 0) > 0,
                            "occupancy_timestamp": occupancy_data.get("timestamp"),
                            "occupancy_stream_id": stream_id
                        })
                        
                        # Log occupancy alerts if any
                        alerts = occupancy_data.get("alerts", [])
                        if alerts:
                            for alert in alerts:
                                level = alert.get('level', 'unknown').upper()
                                message = alert.get('message', 'No message')
                                logger.info(f"🚨 Occupancy Alert [{level}]: {message}")
                        
                        # Log density heatmap generation
                        if occupancy_data.get("density_heatmap"):
                            logger.info("📊 Density heatmap generated and sent to frontend")
                            
                    except Exception as occ_err:
                        logger.error(f"Error processing occupancy data: {occ_err}")
                    
                    # Send response to frontend
                    await websocket.send_json(response_data)
                    
                except Exception as frame_err:
                    logger.error(f"Frame processing error: {frame_err}")
                    await websocket.send_json({
                        "success": False,
                        "error": f"Frame processing failed: {str(frame_err)}"
                    })
                    
    except WebSocketDisconnect:
        logger.info("❌ External camera WebSocket disconnected")
    except Exception as e:
        logger.error(f"External camera WebSocket error: {e}")
        try:
            await websocket.send_json({
                "success": False,
                "error": str(e)
            })
        except:
            pass
    finally:
        # Clean up demo video capture if it was used
        if demo_video_cap is not None:
            demo_video_cap.release()
            logger.info("🎬 Demo video capture released")

@app.websocket("/ws/video-process")
async def websocket_video_process(websocket: WebSocket):
    """WebSocket endpoint for video file processing with frame-by-frame analysis"""
    await websocket.accept()
    logger.info("✅ WebSocket connected for video processing")
    
    try:
        # Wait for initial configuration message
        config_data = await websocket.receive_json()
        
        model_type = config_data.get("model", "yolo-nano")
        enable_tracking = config_data.get("tracking", True)
        confidence_threshold = config_data.get("confidence", 0.5)
        
        logger.info(f"📹 Video processing config: model={model_type}, tracking={enable_tracking}")
        
        await websocket.send_json({
            "status": "ready",
            "message": "Ready to receive video frames",
            "config": {
                "model": model_type,
                "tracking": enable_tracking,
                "confidence": confidence_threshold
            }
        })
        
        # Map model variants
        yolo_model_map = {
            "yolo": "yolov8n.pt",
            "yolo-nano": "yolov8n.pt",
            "yolo-small": "yolov8s.pt",
            "yolo-medium": "yolov8m.pt",
            "yolo-large": "yolov8l.pt"
        }
        
        frame_number = 0
        
        # Process frames as they arrive
        while True:
            try:
                data = await websocket.receive_json()
                
                # Check if it's a frame or control message
                if data.get("action") == "close":
                    logger.info("Client requested to close video processing")
                    break
                
                frame_data = data.get("frame")
                if not frame_data:
                    continue
                
                frame_number += 1
                
                # Decode frame
                import base64
                if frame_data.startswith("data:image"):
                    frame_data = frame_data.split(",")[1]
                
                image_bytes = base64.b64decode(frame_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Convert to numpy for processing
                img_array = np.array(image)
                if img_array.shape[-1] == 3:  # RGB
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Process based on model type
                result = {}
                
                if model_type.lower() in yolo_model_map:
                    # Use YOLO with tracking if enabled
                    if enable_tracking and UnifiedCounter is not None:
                        try:
                            checkpoint = yolo_model_map[model_type.lower()]
                            counter = get_tracking_counter(checkpoint, source="video")
                            
                            if counter is not None:
                                result = counter.predict(
                                    img_array,
                                    return_details=True,
                                    return_visualization=True
                                )
                                model_name = f"YOLO-{checkpoint.replace('.pt', '').replace('yolov8', '').upper()}-Tracking"
                                
                                # Add advanced metrics if available
                                try:
                                    frame_shape = (img_array.shape[0], img_array.shape[1])
                                    advanced_metrics = counter.get_advanced_metrics(
                                        frame_shape=frame_shape,
                                        frame_rate=30,
                                        frame_step=25
                                    )
                                    if advanced_metrics:
                                        result["advanced_metrics"] = advanced_metrics
                                except Exception as adv_err:
                                    logger.warning(f"Advanced metrics error: {adv_err}")
                            else:
                                # Fallback to regular YOLO
                                result = yolo_api.predict(
                                    image,
                                    checkpoint_path=checkpoint,
                                    return_boxes=True,
                                    visualize=True
                                ) if yolo_api else {"count": 0}
                                model_name = f"YOLO-{checkpoint.replace('.pt', '').replace('yolov8', '').upper()}"
                        except Exception as e:
                            logger.error(f"YOLO tracking error: {e}")
                            result = {"count": 0, "error": str(e)}
                            model_name = "YOLO-ERROR"
                    else:
                        # Regular YOLO without tracking
                        checkpoint = yolo_model_map.get(model_type.lower(), "yolov8n.pt")
                        result = yolo_api.predict(
                            image,
                            checkpoint_path=checkpoint,
                            return_boxes=True,
                            visualize=True
                        ) if yolo_api else {"count": 0}
                        model_name = f"YOLO-{checkpoint.replace('.pt', '').replace('yolov8', '').upper()}"
                
                elif model_type.lower() == "csrnet":
                    result = csrnet_api.predict(image, source="video") if csrnet_api else {"count": 0}
                    model_name = "CSRNet"
                
                else:
                    result = {"count": 0, "error": "Unknown model"}
                    model_name = "Unknown"
                
                # Build response
                response = {
                    "success": True,
                    "frame_number": frame_number,
                    "model": model_name.lower(),
                    "count": result.get("count", result.get("rounded_count", 0)),
                    "inference_time_ms": result.get("inference_time_ms", 0),
                    "fps": 1000 / result["inference_time_ms"] if result.get("inference_time_ms", 0) > 0 else 0,
                    "timestamp": data.get("timestamp", 0)
                }
                
                # Add YOLO-specific data
                if model_type.lower() in yolo_model_map:
                    response["boxes"] = result.get("boxes", [])
                    response["num_detections"] = len(result.get("boxes", []))
                    
                    # Add tracking data if enabled
                    if enable_tracking:
                        response["unique_count"] = result.get("unique_count", response["count"])
                        response["tracks"] = result.get("tracks", [])
                        
                        if "speed_stats" in result:
                            response["speed_stats"] = result["speed_stats"]
                        
                        if "advanced_metrics" in result:
                            response["advanced_metrics"] = result["advanced_metrics"]
                    
                    # Add heatmap/annotated image
                    if "annotated_image" in result:
                        annotated_bgr = result["annotated_image"]
                        _, buffer = cv2.imencode('.jpg', annotated_bgr)
                        img_base64 = base64.b64encode(buffer).decode()
                        response["annotated_frame"] = f"data:image/jpeg;base64,{img_base64}"
                        logger.info("📷 Annotated frame with trajectories sent to frontend")
                
                await websocket.send_json(response)
                
            except WebSocketDisconnect:
                logger.info("Client disconnected during video processing")
                break
            except Exception as frame_error:
                logger.error(f"Frame processing error: {frame_error}")
                await websocket.send_json({
                    "success": False,
                    "error": f"Frame processing failed: {str(frame_error)}",
                    "frame_number": frame_number
                })
        
    except WebSocketDisconnect:
        logger.info("❌ Video processing WebSocket disconnected")
    except Exception as e:
        logger.error(f"Video processing WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "success": False,
                "error": str(e)
            })
        except:
            pass


@app.websocket("/ws/pedestrian-track")
async def websocket_pedestrian_track(websocket: WebSocket):
    """WebSocket endpoint for real-time pedestrian tracking from video frames"""
    await websocket.accept()
    logger.info("✅ WebSocket connected for pedestrian tracking")
    
    tracker = None
    frame_number = 0
    
    try:
        # Wait for initial configuration
        config_data = await websocket.receive_json()
        
        homography_data = config_data.get("homography")
        model_path = config_data.get("model_path", "yolov8n.pt")
        
        logger.info(f"📊 Pedestrian tracking config: model={model_path}, homography={homography_data is not None}")
        
        # Initialize tracker with visualization
        if PedestrianTracker is not None:
            # Extract visualization settings from config
            trajectory_max_points = config_data.get("trajectory_max_points", 30)
            trajectory_max_distance_cm = config_data.get("trajectory_max_distance_cm", 2.0)
            
            tracker = PedestrianTracker(
                model_path=model_path,
                trajectory_max_points=trajectory_max_points,
                trajectory_max_distance_cm=trajectory_max_distance_cm,
                enable_visualization=True
            )
            logger.info(f"✅ Tracker initialized with trajectory points: {trajectory_max_points}")
            
            # Set homography if provided
            if homography_data:
                tracker.set_homography(
                    homography_data.get("image_points", []),
                    homography_data.get("world_points", [])
                )
            
            await websocket.send_json({
                "status": "ready",
                "message": "Pedestrian tracker ready",
                "config": {
                    "model": model_path,
                    "homography": homography_data is not None,
                    "trajectory_max_points": trajectory_max_points,
                    "trajectory_max_distance_cm": trajectory_max_distance_cm
                }
            })
        else:
            await websocket.send_json({
                "status": "error",
                "message": "Pedestrian tracker not available"
            })
            return
        
        # Process frames
        while True:
            try:
                data = await websocket.receive_json()
                
                # Check for control messages
                if data.get("action") == "close":
                    logger.info("Client requested to close pedestrian tracking")
                    break
                
                frame_data = data.get("frame")
                if not frame_data:
                    continue
                
                # Decode frame
                if frame_data.startswith("data:image"):
                    frame_data = frame_data.split(",")[1]
                
                image_bytes = base64.b64decode(frame_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Convert to numpy
                img_array = np.array(image)
                if img_array.shape[-1] == 3:  # RGB
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Extract trajectory settings from data (from frontend slider)
                max_trajectory_points = data.get("max_trajectory_points", 30)
                
                # Process frame with visualization
                result = tracker.process_frame(
                    img_array, 
                    frame_number,
                    max_trajectory_points=max_trajectory_points,
                    annotate=True
                )
                
                frame_number += 1
                
                # Send response
                response = {
                    "success": True,
                    "frame_number": frame_number,
                    "count": result.get("count", 0),
                    "unique_count": result.get("unique_count", 0),
                    "trajectories": result.get("trajectories", {}),
                    "use_world_coords": result.get("use_world_coords", False),
                    "trajectory_max_points": max_trajectory_points
                }
                
                # Encode annotated frame if available
                if "annotated_frame" in result and result["annotated_frame"] is not None:
                    _, buffer = cv2.imencode(".jpg", result["annotated_frame"])
                    frame_base64 = base64.b64encode(buffer.tobytes()).decode()
                    response["frame"] = f"data:image/jpeg;base64,{frame_base64}"
                
                await websocket.send_json(response)
                
            except Exception as e:
                logger.error(f"Error processing pedestrian tracking frame: {e}")
                await websocket.send_json({
                    "success": False,
                    "error": str(e),
                    "frame_number": frame_number
                })
                continue
    
    except WebSocketDisconnect:
        logger.info("❌ Pedestrian tracking WebSocket disconnected")
        if tracker:
            metrics = tracker.get_metrics()
            logger.info(f"Final metrics: {metrics}")
    except Exception as e:
        logger.error(f"Pedestrian tracking WebSocket error: {e}", exc_info=True)
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
