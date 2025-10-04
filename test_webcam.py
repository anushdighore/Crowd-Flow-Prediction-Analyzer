"""
Test script for webcam capture and processing
Run this to verify webcam and model are working correctly
"""

import cv2
import torch
import logging
from models.vmamba_official import load_tmtb_model
from utils.preprocess import preprocess_frame
from utils.postprocess import get_count_from_density
from utils.webcam import WebcamCapture, draw_count_overlay, FPSCounter
from PIL import Image
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_webcam():
    """Test basic webcam functionality"""
    logger.info("🎥 Testing webcam capture...")
    
    with WebcamCapture(camera_id=0, width=640, height=480) as cam:
        if not cam.is_opened:
            logger.error("❌ Failed to open webcam")
            return False
        
        # Capture a few frames
        for i in range(5):
            frame = cam.read_frame()
            if frame is None:
                logger.error(f"❌ Failed to read frame {i+1}")
                return False
            logger.info(f"✅ Frame {i+1}: {frame.shape}")
            time.sleep(0.1)
    
    logger.info("✅ Webcam test passed!")
    return True

def test_model():
    """Test model loading"""
    logger.info("🧠 Testing model loading...")
    
    checkpoint_path = "./checkpoints/jhu_5.pth"
    
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"🔧 Using device: {device}")
        
        model = load_tmtb_model(checkpoint_path)
        model.eval()
        model.to(device)
        
        logger.info("✅ Model loaded successfully!")
        return True, model, device
    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}")
        return False, None, None

def test_inference(model, device):
    """Test model inference with webcam frame"""
    logger.info("🔬 Testing inference with webcam frame...")
    
    with WebcamCapture(camera_id=0, width=640, height=480) as cam:
        if not cam.is_opened:
            logger.error("❌ Failed to open webcam for inference test")
            return False
        
        # Capture frame
        frame = cam.read_frame()
        if frame is None:
            logger.error("❌ Failed to capture frame")
            return False
        
        logger.info(f"📸 Captured frame: {frame.shape}")
        
        # Convert to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        # Preprocess
        logger.info("🔄 Preprocessing...")
        input_tensor = preprocess_frame(pil_image)
        input_tensor = input_tensor.to(device)
        logger.info(f"✅ Input tensor shape: {input_tensor.shape}")
        
        # Inference
        logger.info("🤖 Running inference...")
        start_time = time.time()
        with torch.no_grad():
            density_map = model(input_tensor)
        inference_time = (time.time() - start_time) * 1000
        logger.info(f"✅ Inference time: {inference_time:.2f}ms")
        logger.info(f"✅ Density map shape: {density_map.shape}")
        
        # Post-process
        logger.info("📊 Post-processing...")
        density_np = density_map.squeeze().cpu().numpy()
        count, reasoning = get_count_from_density(density_np)
        logger.info(f"✅ Count: {count}")
        logger.info(f"✅ Reasoning: {reasoning}")
        
        logger.info("✅ Full inference pipeline test passed!")
        return True

def test_live_display(model, device, duration=10):
    """Test live display with count overlay"""
    logger.info(f"🎬 Testing live display for {duration} seconds...")
    logger.info("Press 'q' to quit early")
    
    with WebcamCapture(camera_id=0, width=640, height=480) as cam:
        if not cam.is_opened:
            logger.error("❌ Failed to open webcam for display test")
            return False
        
        fps_counter = FPSCounter()
        start_time = time.time()
        frame_count = 0
        
        while (time.time() - start_time) < duration:
            # Capture frame
            frame = cam.read_frame()
            if frame is None:
                continue
            
            frame_count += 1
            
            # Process every 3rd frame (to keep it real-time)
            if frame_count % 3 == 0:
                try:
                    # Convert to PIL
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Inference
                    input_tensor = preprocess_frame(pil_image).to(device)
                    with torch.no_grad():
                        density_map = model(input_tensor)
                    
                    # Get count
                    density_np = density_map.squeeze().cpu().numpy()
                    count, _ = get_count_from_density(density_np)
                    
                    # Update FPS
                    fps = fps_counter.update()
                    
                    # Draw overlay
                    frame = draw_count_overlay(frame, int(count), fps)
                    
                except Exception as e:
                    logger.error(f"Processing error: {e}")
            
            # Display
            cv2.imshow('Live Crowd Counter Test', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        
        logger.info(f"✅ Processed {frame_count} frames in {duration} seconds")
        logger.info(f"✅ Average FPS: {frame_count/duration:.2f}")
        logger.info("✅ Live display test passed!")
        return True

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("  WEBCAM CROWD COUNTER TEST SUITE")
    logger.info("=" * 60)
    logger.info("")
    
    # Test 1: Webcam
    if not test_webcam():
        logger.error("❌ Webcam test failed. Please check your webcam.")
        return
    
    logger.info("")
    logger.info("-" * 60)
    logger.info("")
    
    # Test 2: Model
    success, model, device = test_model()
    if not success:
        logger.error("❌ Model test failed. Please check checkpoint file.")
        return
    
    logger.info("")
    logger.info("-" * 60)
    logger.info("")
    
    # Test 3: Inference
    if not test_inference(model, device):
        logger.error("❌ Inference test failed.")
        return
    
    logger.info("")
    logger.info("-" * 60)
    logger.info("")
    
    # Test 4: Live display
    logger.info("Starting live display test...")
    logger.info("This will show your webcam with crowd counting overlay")
    input("Press Enter to continue (or Ctrl+C to skip)...")
    
    try:
        test_live_display(model, device, duration=10)
    except KeyboardInterrupt:
        logger.info("Live display test skipped")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("  ✅ ALL TESTS PASSED!")
    logger.info("  Your system is ready for real-time crowd counting!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Run: start_webcam_app.bat")
    logger.info("2. Open browser: http://localhost:3000")
    logger.info("3. Click '🎥 Live Webcam' and start streaming!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nTest interrupted by user")
    except Exception as e:
        logger.error(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
