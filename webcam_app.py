from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.vmamba_official import load_tmtb_model
from utils.preprocess import preprocess_frame
from utils.postprocess import get_count_from_density
import cv2
import numpy as np
import torch
import time
import logging
import base64
import json
from PIL import Image
import io
from typing import Dict, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Webcam Crowd Counter",
    description="VMamba-TMTB based real-time crowd counting with webcam support",
    version="2.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model and device variables
model = None
device = None

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

manager = ConnectionManager()


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
        model = load_tmtb_model(checkpoint_path)
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
        "message": "Real-Time Webcam Crowd Counter API",
        "status": status,
        "device": str(device) if device else "Unknown",
        "endpoints": ["/health", "/ws/count"]
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Detailed health check"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "device": str(device) if device else "Unknown",
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "active_connections": len(manager.active_connections)
    }


def process_frame(frame_data: str) -> Dict[str, Any]:
    """
    Process a single frame from webcam
    
    Args:
        frame_data: Base64 encoded image data
        
    Returns:
        Dictionary with count and processing time
    """
    try:
        start_time = time.time()
        
        # Decode base64 image
        if ',' in frame_data:
            frame_data = frame_data.split(',')[1]
        
        image_bytes = base64.b64decode(frame_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Preprocess
        preprocess_start = time.time()
        input_tensor = preprocess_frame(image)
        input_tensor = input_tensor.to(device)
        preprocess_time = (time.time() - preprocess_start) * 1000
        
        # Model inference
        inference_start = time.time()
        with torch.no_grad():
            density_map = model(input_tensor)
        inference_time = (time.time() - inference_start) * 1000
        
        # Post-process
        postprocess_start = time.time()
        density_np = density_map.squeeze().cpu().numpy()
        count, reasoning = get_count_from_density(density_np)
        postprocess_time = (time.time() - postprocess_start) * 1000
        
        total_time = (time.time() - start_time) * 1000
        
        # Calculate FPS
        fps = 1000 / total_time if total_time > 0 else 0
        
        return {
            "success": True,
            "count": int(count),
            "reasoning": reasoning,
            "fps": round(fps, 2),
            "timing": {
                "preprocess_ms": round(preprocess_time, 2),
                "inference_ms": round(inference_time, 2),
                "postprocess_ms": round(postprocess_time, 2),
                "total_ms": round(total_time, 2)
            },
            "image_size": f"{image.width}x{image.height}",
            "density_map_stats": {
                "min": float(density_np.min()),
                "max": float(density_np.max()),
                "mean": float(density_np.mean()),
                "sum": float(density_np.sum())
            }
        }
        
    except Exception as e:
        logger.error(f"Frame processing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "count": 0
        }


@app.websocket("/ws/count")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time frame processing
    
    Client sends: {"frame": "base64_encoded_image"}
    Server responds: {"success": true, "count": X, "fps": Y, ...}
    """
    await manager.connect(websocket)
    
    try:
        # Check if model is loaded
        if model is None:
            await manager.send_json(websocket, {
                "success": False,
                "error": "Model not loaded"
            })
            return
        
        frame_count = 0
        
        while True:
            # Receive frame data
            data = await websocket.receive_text()
            frame_count += 1
            
            try:
                # Parse JSON
                frame_message = json.loads(data)
                frame_data = frame_message.get("frame", "")
                
                if not frame_data:
                    await manager.send_json(websocket, {
                        "success": False,
                        "error": "No frame data received"
                    })
                    continue
                
                # Process frame
                result = process_frame(frame_data)
                result["frame_number"] = frame_count
                
                # Send result back
                await manager.send_json(websocket, result)
                
                # Log every 30 frames
                if frame_count % 30 == 0:
                    logger.info(f"📹 Processed {frame_count} frames | Count: {result.get('count', 0)} | FPS: {result.get('fps', 0)}")
                
            except json.JSONDecodeError:
                await manager.send_json(websocket, {
                    "success": False,
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error processing frame {frame_count}: {e}")
                await manager.send_json(websocket, {
                    "success": False,
                    "error": str(e),
                    "frame_number": frame_count
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"🔌 Client disconnected after {frame_count} frames")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Real-Time Webcam Crowd Counter Server")
    logger.info("📡 WebSocket endpoint: ws://localhost:8000/ws/count")
    logger.info("🌐 Health check: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
