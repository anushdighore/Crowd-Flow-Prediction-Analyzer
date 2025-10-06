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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="CSRNet Crowd Counting API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
device = None

# Preprocessing transform - EXACTLY as per CSRNet paper
transform = transforms.Compose([
    transforms.ToTensor(),  # Converts [0,255] to [0.0, 1.0]
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # ImageNet mean
        std=[0.229, 0.224, 0.225]     # ImageNet std
    )
])


@app.on_event("startup")
async def load_model():
    """Load model on startup"""
    global model, device
    
    logger.info("🚀 Starting CSRNet API Server...")
    
    # Detect device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"🖥️  Device: {device}")
    
    # Load model
    checkpoint_path = "./checkpoint/csrnet.pth"
    try:
        model = load_csrnet(checkpoint_path, device=device)
        logger.info("✅ Model loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "running",
        "message": "CSRNet Crowd Counting API",
        "model_loaded": model is not None,
        "device": str(device)
    }


@app.post("/count")
async def count_people(file: UploadFile = File(...)):
    """
    Count people in uploaded image
    
    Returns:
        JSON with crowd count
    """
    logger.info("="*60)
    logger.info(f"📸 Received: {file.filename}")
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Invalid file type")
    
    # Load image
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        orig_width, orig_height = image.size
        logger.info(f"📐 Image size: {orig_width}x{orig_height}")
    except Exception as e:
        logger.error(f"❌ Error loading image: {e}")
        raise HTTPException(400, "Could not read image")
    
    # Preprocess
    try:
        logger.info("🔧 Preprocessing...")
        image_tensor = transform(image).unsqueeze(0)  # Add batch dim
        image_tensor = image_tensor.to(device)
        logger.info(f"   Tensor shape: {list(image_tensor.shape)}")
        logger.info(f"   Tensor range: [{image_tensor.min():.3f}, {image_tensor.max():.3f}]")
    except Exception as e:
        logger.error(f"❌ Preprocessing failed: {e}")
        raise HTTPException(500, "Preprocessing failed")
    
    # Inference
    try:
        logger.info("🧠 Running inference...")
        
        with torch.no_grad():
            model.eval()  # Ensure eval mode
            density_map = model(image_tensor)
        
        # Get count
        crowd_count = density_map.sum().item()
        
        logger.info(f"   Density map shape: {list(density_map.shape)}")
        logger.info(f"   Density map range: [{density_map.min().item():.4f}, {density_map.max().item():.4f}]")
        logger.info(f"   Raw count: {crowd_count:.2f}")
        
        # Round to nearest integer
        crowd_count = int(round(crowd_count))
        
        logger.info(f"✅ Final count: {crowd_count}")
        logger.info("="*60)
        
        return {
            "success": True,
            "count": crowd_count,
            "image_size": f"{orig_width}x{orig_height}",
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Inference failed: {str(e)}")


@app.get("/health")
async def health():
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
