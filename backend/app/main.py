"""
Crowd Counter Backend API

Main FastAPI application for crowd counting models.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
from PIL import Image
import io
import sys
from pathlib import Path
import torch

# Add ml/src to path
ml_path = Path(__file__).parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))

from models.csrnet import api as csrnet_api
from models.tmtb.vmamba_official import load_tmtb_model

# Import API router
from app.api import api_router

# Global TMTB model cache
_tmtb_model = None
_tmtb_device = None
_tmtb_transform = None


def get_tmtb_model():
    """Get or initialize TMTB model"""
    global _tmtb_model, _tmtb_device, _tmtb_transform
    if _tmtb_model is None:
        import torchvision.transforms as transforms
        _tmtb_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        checkpoint_path = Path(__file__).parent.parent / "ml" / "checkpoints" / "jhu_5.pth"
        _tmtb_model = load_tmtb_model(str(checkpoint_path), device=str(_tmtb_device))
        _tmtb_model.eval()
        _tmtb_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        logger.info("✅ TMTB model loaded for WebSocket")
    return _tmtb_model, _tmtb_transform, _tmtb_device

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crowd Counter API",
    description="Multi-model crowd counting API with CSRNet, VMamba, and more",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Crowd Counter API",
        "version": "1.0.0",
        "models": ["CSRNet", "TMTB (VMamba)"],
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Crowd Counter API"
    }


# WebSocket endpoint for real-time counting
@app.websocket("/ws/count")
async def websocket_count(websocket: WebSocket):
    """WebSocket endpoint for real-time webcam counting"""
    await websocket.accept()
    logger.info("✅ WebSocket connected for real-time counting")
    
    frame_number = 0
    
    try:
        while True:
            # Receive image data from frontend
            data = await websocket.receive_json()
            
            # Extract frame data (frontend sends "frame" key)
            frame_data = data.get("frame") or data.get("image")
            model_type = data.get("model", "csrnet")
            
            if not frame_data:
                await websocket.send_json({
                    "success": False,
                    "error": "No frame data received"
                })
                continue
            
            # Decode base64 image
            import base64
            if frame_data.startswith("data:image"):
                frame_data = frame_data.split(",")[1]
            
            image_bytes = base64.b64decode(frame_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Run prediction based on selected model
            if model_type.lower() == "tmtb":
                # Use TMTB model
                tmtb_model, tmtb_transform, tmtb_device = get_tmtb_model()
                image_tensor = tmtb_transform(image).unsqueeze(0).to(tmtb_device)
                
                with torch.no_grad():
                    output = tmtb_model(image_tensor)
                    if isinstance(output, tuple):
                        density_map = output[0]
                    else:
                        density_map = output
                    count = density_map.sum().item()
                
                result = {
                    "count": round(count),
                    "inference_time_ms": 0  # TMTB doesn't track time yet
                }
                model_name = "TMTB"
            else:
                # Use CSRNet (default)
                result = csrnet_api.predict(image, max_size=640)
                model_name = "CSRNet"
            
            frame_number += 1
            
            # Send result (match frontend expected format)
            await websocket.send_json({
                "success": True,
                "model": model_name.lower(),
                "count": result["count"] if "count" in result else result.get("rounded_count", 0),
                "inference_time_ms": result.get("inference_time_ms", 0),
                "frame_number": frame_number,
                "fps": 1000 / result["inference_time_ms"] if result.get("inference_time_ms", 0) > 0 else 0
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )