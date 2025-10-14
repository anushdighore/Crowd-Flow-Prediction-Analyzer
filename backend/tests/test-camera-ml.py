"""
Test Camera + ML Integration
Captures video from camera, sends to CSRNet endpoint, and displays predictions in browser.
Access via: http://localhost:8001/stream
"""

import asyncio
import io
import logging
import sys
import time
from pathlib import Path

import aiohttp
import cv2
import numpy as np
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Camera ML Test")

# Global variables
CAMERA_URL = "http://192.168.137.209:8080/video"  # Change to your camera URL
CSRNET_ENDPOINT = "http://localhost:8000/api/v1/csrnet/webcam"
current_count = 0
inference_time = 0.0
last_error = None


async def get_frame_from_camera():
    """Get a frame from the camera"""
    try:
        # Use direct aiohttp instead of CameraClient for more flexibility
        timeout = aiohttp.ClientTimeout(total=5.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(CAMERA_URL) as response:
                if response.status != 200:
                    logger.error(f"Camera returned status {response.status}")
                    return None
                
                # Get image data directly
                img_data = await response.read()
                if not img_data:
                    logger.error("Received empty image data")
                    return None
                
                # Convert to numpy array and decode
                nparr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None and frame.size > 0:
                    return frame
                else:
                    logger.error("Failed to decode camera image")
                    return None
                    
    except Exception as e:
        logger.error(f"Error getting frame: {e}")
        return None


async def send_to_csrnet(frame: np.ndarray):
    """Send frame to CSRNet endpoint and get prediction"""
    global current_count, inference_time, last_error
    
    try:
        # Convert frame to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)
        
        # Send to CSRNet endpoint
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field('file', img_byte_arr, filename='frame.jpg', content_type='image/jpeg')
            
            async with session.post(CSRNET_ENDPOINT, data=form_data) as response:
                if response.status == 200:
                    result = await response.json()
                    current_count = result.get('count', 0)
                    inference_time = result.get('inference_time_ms', 0.0)
                    last_error = None
                    logger.info(f"✅ Count: {current_count}, Inference: {inference_time:.2f}ms")
                    return result
                else:
                    error_text = await response.text()
                    last_error = f"HTTP {response.status}: {error_text}"
                    logger.error(f"CSRNet error: {last_error}")
                    return None
                    
    except Exception as e:
        last_error = str(e)
        logger.error(f"Error sending to CSRNet: {e}")
        return None


async def generate_annotated_stream():
    """Generate MJPEG stream with ML predictions overlaid"""
    global current_count, inference_time, last_error
    
    frame_count = 0
    process_every_n_frames = 5  # Process every 5th frame for ML
    
    while True:
        try:
            # Get frame from camera
            frame = await get_frame_from_camera()
            
            if frame is None:
                # Show error frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera Error", (50, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            else:
                # Process with ML every N frames
                if frame_count % process_every_n_frames == 0:
                    asyncio.create_task(send_to_csrnet(frame))
                
                # Overlay predictions on frame
                h, w = frame.shape[:2]
                
                # Semi-transparent overlay at top
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, 120), (0, 0, 0), -1)
                frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
                
                # Display count
                count_text = f"People Count: {current_count}"
                cv2.putText(frame, count_text, (20, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                
                # Display inference time
                time_text = f"Inference: {inference_time:.1f}ms"
                cv2.putText(frame, time_text, (20, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Display error if any
                if last_error:
                    cv2.putText(frame, f"Error: {last_error[:50]}", (20, h - 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            frame_bytes = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            frame_count += 1
            await asyncio.sleep(0.033)  # ~30 FPS
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            await asyncio.sleep(1)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve HTML page with video stream"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera + ML Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                max-width: 1000px;
                width: 100%;
            }
            h1 {
                color: #333;
                margin-top: 0;
                text-align: center;
            }
            .video-container {
                background: #000;
                border-radius: 8px;
                overflow: hidden;
                margin: 20px 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            img {
                width: 100%;
                height: auto;
                display: block;
            }
            .info-box {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                margin-top: 20px;
            }
            .info-box h3 {
                margin-top: 0;
                color: #667eea;
            }
            .info-box ul {
                margin: 10px 0;
                padding-left: 20px;
            }
            .info-box li {
                margin: 8px 0;
                color: #555;
            }
            .status {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            .status.active {
                background: #d4edda;
                color: #155724;
            }
            code {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎥 Camera + ML Integration Test</h1>
            
            <div class="video-container">
                <img src="/stream" alt="Camera Stream with ML Predictions">
            </div>
            
            <div class="info-box">
                <h3>📊 System Status</h3>
                <ul>
                    <li><strong>Status:</strong> <span class="status active">Active</span></li>
                    <li><strong>Camera URL:</strong> <code>""" + CAMERA_URL + """</code></li>
                    <li><strong>ML Endpoint:</strong> <code>""" + CSRNET_ENDPOINT + """</code></li>
                    <li><strong>Model:</strong> CSRNet (Crowd Counting)</li>
                    <li><strong>Processing:</strong> Every 5th frame (~6 FPS)</li>
                </ul>
            </div>
            
            <div class="info-box">
                <h3>ℹ️ Instructions</h3>
                <ul>
                    <li>The stream shows live camera feed with ML predictions overlaid</li>
                    <li>Green text shows the current people count</li>
                    <li>White text shows inference time in milliseconds</li>
                    <li>Predictions update automatically every ~166ms</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/stream")
async def video_stream():
    """MJPEG video stream endpoint"""
    return StreamingResponse(
        generate_annotated_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/test-csrnet")
async def test_csrnet():
    """Test CSRNet endpoint directly"""
    try:
        # Create a simple test image (black 224x224 image)
        test_image = np.zeros((224, 224, 3), dtype=np.uint8)
        pil_image = Image.fromarray(test_image)
        
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)
        
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field('file', img_byte_arr, filename='test.jpg', content_type='image/jpeg')
            
            async with session.post(CSRNET_ENDPOINT, data=form_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "success",
                        "message": "CSRNet API is working!",
                        "result": result
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "message": f"CSRNet API returned {response.status}",
                        "details": error_text
                    }
                    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing CSRNet API: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("🚀 Starting Camera + ML Test Server")
    logger.info("=" * 60)
    logger.info(f"📹 Camera URL: {CAMERA_URL}")
    logger.info(f"🤖 ML Endpoint: {CSRNET_ENDPOINT}")
    logger.info(f"🌐 Web Interface: http://localhost:8001")
    logger.info(f"📺 Direct Stream: http://localhost:8001/stream")
    logger.info(f"🧪 Test CSRNet API: http://localhost:8001/test-csrnet")
    logger.info(f"📊 Stats API: http://localhost:8001/stats")
    logger.info("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
