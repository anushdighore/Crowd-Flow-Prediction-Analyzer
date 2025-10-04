"""
Multi-Model Real-Time Webcam Crowd Counter API
Supports: VMamba-TMTB, CSRNet, YOLOv8, MCNN
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models.model_factory import ModelFactory
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
from typing import Dict, Any, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Model Webcam Crowd Counter",
    description="Real-time crowd counting with multiple model architectures",
    version="3.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model state
current_model = None
current_model_type = "vmamba_tmtb"  # Default model
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


class ModelSelection(BaseModel):
    """Model selection request"""
    model_type: str
    checkpoint_path: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Load default model on application startup"""
    global current_model, device, current_model_type
    
    logger.info("🚀 Starting Multi-Model Webcam Crowd Counter Server")
    logger.info("📡 WebSocket endpoint: ws://localhost:8000/ws/count")
    logger.info("🌐 Health check: http://localhost:8000/health")
    logger.info("🔧 Model selection: POST http://localhost:8000/api/select-model")
    
    # Initialize device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"🔧 Using device: {device}")
    
    # Load default model
    try:
        await load_model(current_model_type)
    except Exception as e:
        logger.error(f"❌ Failed to load default model: {e}")
        current_model = None


async def load_model(model_type: str, checkpoint_path: Optional[str] = None):
    """Load a specific model"""
    global current_model, current_model_type
    
    try:
        logger.info(f"🔄 Loading model: {model_type}")
        
        # Get model info
        model_info = ModelFactory.get_model_info(model_type)
        checkpoint = checkpoint_path or model_info['checkpoint']
        
        # Create model
        current_model = ModelFactory.create_model(
            model_type=model_type,
            checkpoint_path=checkpoint,
            device=str(device)
        )
        
        current_model_type = model_type
        
        # Log model parameters for PyTorch models
        if hasattr(current_model, 'parameters'):
            total_params = sum(p.numel() for p in current_model.parameters())
            logger.info(f"📊 Model parameters: {total_params:,}")
        
        logger.info(f"✅ {model_info['name']} loaded successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to load model {model_type}: {e}")
        raise


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "message": "Multi-Model Webcam Crowd Counter API",
        "status": "Model loaded" if current_model is not None else "Model not loaded",
        "current_model": current_model_type,
        "device": str(device) if device else "Unknown",
        "endpoints": [
            "/health",
            "/api/models",
            "/api/current-model",
            "/api/select-model",
            "/ws/count"
        ]
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Detailed health check"""
    return {
        "status": "healthy" if current_model is not None else "unhealthy",
        "model_loaded": current_model is not None,
        "current_model": current_model_type,
        "device": str(device) if device else "Unknown",
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "active_connections": len(manager.active_connections)
    }


@app.get("/api/models")
async def list_models() -> Dict[str, Any]:
    """List all available models"""
    models = ModelFactory.list_available_models()
    
    # Check which models have checkpoints available
    for model_id, model_info in models.items():
        checkpoint_path = model_info['checkpoint']
        model_info['checkpoint_exists'] = os.path.exists(checkpoint_path)
    
    return {
        "models": models,
        "current_model": current_model_type
    }


@app.get("/api/current-model")
async def get_current_model() -> Dict[str, Any]:
    """Get current model information"""
    if current_model is None:
        raise HTTPException(status_code=500, detail="No model loaded")
    
    model_info = ModelFactory.get_model_info(current_model_type)
    
    return {
        "model_type": current_model_type,
        "model_info": model_info,
        "device": str(device)
    }


@app.post("/api/select-model")
async def select_model(selection: ModelSelection) -> Dict[str, Any]:
    """
    Select and load a different model
    
    Args:
        selection: ModelSelection with model_type and optional checkpoint_path
        
    Returns:
        Status of model loading
    """
    try:
        await load_model(selection.model_type, selection.checkpoint_path)
        
        return {
            "success": True,
            "message": f"Model switched to {selection.model_type}",
            "current_model": current_model_type,
            "model_info": ModelFactory.get_model_info(current_model_type)
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to switch model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def process_frame_with_yolov8(frame_data: str) -> Dict[str, Any]:
    """Process frame with YOLOv8 model"""
    try:
        start_time = time.time()
        
        # Decode base64 image
        if ',' in frame_data:
            frame_data = frame_data.split(',')[1]
        
        image_bytes = base64.b64decode(frame_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB numpy array
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_np = np.array(image)
        
        # Run YOLOv8 prediction
        result = current_model.predict(image_np, return_boxes=False)
        
        total_time = (time.time() - start_time) * 1000
        fps = 1000 / total_time if total_time > 0 else 0
        
        return {
            "success": True,
            "count": result['count'],
            "reasoning": f"Detected {result['count']} persons using YOLOv8",
            "fps": round(fps, 2),
            "timing": {
                "total_ms": round(total_time, 2)
            },
            "image_size": f"{image.width}x{image.height}",
            "model_type": "yolov8"
        }
    
    except Exception as e:
        logger.error(f"Error processing frame with YOLOv8: {e}")
        return {
            "success": False,
            "error": str(e),
            "count": 0
        }


def process_frame_with_density_model(frame_data: str) -> Dict[str, Any]:
    """Process frame with density-based models (VMamba, CSRNet, MCNN)"""
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
            density_map = current_model(input_tensor)
        inference_time = (time.time() - inference_start) * 1000
        
        # Post-process
        postprocess_start = time.time()
        density_np = density_map.squeeze().cpu().numpy()
        count, reasoning = get_count_from_density(density_np)
        postprocess_time = (time.time() - postprocess_start) * 1000
        
        total_time = (time.time() - start_time) * 1000
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
            },
            "model_type": current_model_type
        }
    
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        return {
            "success": False,
            "error": str(e),
            "count": 0
        }


@app.websocket("/ws/count")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time crowd counting
    Receives base64 encoded frames and returns count predictions
    """
    await manager.connect(websocket)
    
    if current_model is None:
        await manager.send_json(websocket, {
            "success": False,
            "error": "Model not loaded"
        })
        return
    
    try:
        while True:
            # Receive frame data from client
            data = await websocket.receive_json()
            frame_data = data.get("frame")
            
            if not frame_data:
                await manager.send_json(websocket, {
                    "success": False,
                    "error": "No frame data received"
                })
                continue
            
            # Process frame based on model type
            if current_model_type == 'yolov8':
                result = process_frame_with_yolov8(frame_data)
            else:
                result = process_frame_with_density_model(frame_data)
            
            # Send result back to client
            await manager.send_json(websocket, result)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("  🎥 MULTI-MODEL WEBCAM CROWD COUNTER")
    print("=" * 60)
    print("📡 WebSocket: ws://localhost:8000/ws/count")
    print("🌐 API Docs: http://localhost:8000/docs")
    print("🔧 Health: http://localhost:8000/health")
    print("📋 Models: http://localhost:8000/api/models")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
