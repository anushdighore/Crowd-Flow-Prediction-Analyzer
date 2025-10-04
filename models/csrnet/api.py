from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import logging
import torch
import torchvision.transforms as transforms
import numpy as np
from csrnet import load_csrnet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CSRNet Crowd Counting API")

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None
device = None

# Image preprocessing transform
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # ImageNet normalization
        std=[0.229, 0.224, 0.225]
    )
])

@app.on_event("startup")
async def load_model():
    """Load CSRNet model on startup"""
    global model, device
    
    logger.info("=" * 50)
    logger.info("🚀 Starting CSRNet API Server...")
    logger.info("=" * 50)
    
    # Detect device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"🖥️  Using device: {device}")
    
    # Load model
    checkpoint_path = "../../checkpoints/csrnet.pth"
    try:
        model = load_csrnet(checkpoint_path=checkpoint_path, device=device)
        logger.info("✅ CSRNet model loaded successfully!")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        logger.error("💡 Make sure checkpoints/csrnet.pth exists!")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "CSRNet Crowd Counting API is active",
        "model_loaded": model is not None,
        "device": str(device)
    }

@app.post("/count")
async def count_people(file: UploadFile = File(...)):
    """
    Count people in uploaded image using CSRNet
    
    Args:
        file: Uploaded image file
        
    Returns:
        JSON with crowd count and metadata
    """
    logger.info("=" * 50)
    logger.info("📸 IMAGE RECEIVED!")
    logger.info(f"Filename: {file.filename}")
    logger.info(f"Content Type: {file.content_type}")
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload an image."
        )
    
    # Read and load image
    try:
        contents = await file.read()
        logger.info(f"File size: {len(contents)} bytes")
        
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        width, height = image.size
        logger.info(f"Image dimensions: {width}x{height}")
        
    except Exception as e:
        logger.error(f"❌ Error loading image: {e}")
        raise HTTPException(status_code=400, detail="Could not read image file.")
    
    # Preprocess image
    try:
        logger.info("🔧 Preprocessing image...")
        image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
        image_tensor = image_tensor.to(device)
        logger.info(f"Tensor shape: {image_tensor.shape}")
        
    except Exception as e:
        logger.error(f"❌ Error preprocessing image: {e}")
        raise HTTPException(status_code=500, detail="Image preprocessing failed.")
    
    # Run inference
    try:
        logger.info("🧠 Running CSRNet inference...")
        
        with torch.no_grad():
            model.eval()
            density_map = model(image_tensor)
            crowd_count = density_map.sum().item()
        
        # Round to nearest integer
        crowd_count = int(round(crowd_count))
        
        logger.info(f"✅ Predicted count: {crowd_count}")
        logger.info("=" * 50)
        
        return {
            "success": True,
            "count": crowd_count,
            "image_size": f"{width}x{height}",
            "filename": file.filename,
            "density_map_shape": list(density_map.shape)
        }
        
    except Exception as e:
        logger.error(f"❌ Error during inference: {e}")
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(device),
        "device_type": "GPU" if torch.cuda.is_available() else "CPU"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
