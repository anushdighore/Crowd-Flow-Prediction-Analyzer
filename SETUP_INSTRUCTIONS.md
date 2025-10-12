# Camera Streaming Setup Instructions

## Quick Start Guide

### 1. Start the Backend Server

**Option A: Using the batch file (Recommended)**
```bash
cd backend
start_server.bat
```

**Option B: Manual start**
```bash
cd backend
conda activate crowdenv
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start the Frontend

```bash
cd frontend
npm start
```

The frontend will open at `http://localhost:3000`

### 3. Using HLS Streaming

1. Click on the **"📺 HLS Streaming"** button in the app
2. Enter your camera URL: `http://192.168.1.6:8080`
3. Click **"Test Camera"** to verify connection
4. Click **"Start HLS Stream"** to begin streaming
5. The video player will automatically load and play the stream

## Camera URL Formats

### IP Camera / Phone Camera Apps
- **IP Webcam (Android)**: `http://192.168.1.6:8080/video`
- **DroidCam**: `http://192.168.1.6:4747/video`
- **Generic snapshot**: `http://192.168.1.6:8080/shot.jpg`

### Testing Camera Connection

Before streaming, test your camera URL:
```bash
# Test if camera is accessible
curl -I http://192.168.1.6:8080
```

## API Endpoints

### Camera Endpoints
- `GET /api/camera/test-connection?camera_url=YOUR_URL` - Test camera connection
- `GET /api/camera/stream?camera_url=YOUR_URL` - MJPEG stream
- `GET /api/camera/process?camera_url=YOUR_URL` - Process single frame

### HLS Streaming Endpoints
- `POST /api/camera/hls/start` - Start HLS streaming
  ```json
  {
    "camera_url": "http://192.168.1.6:8080"
  }
  ```
- `POST /api/camera/hls/stop/{stream_id}` - Stop streaming
- `GET /api/camera/hls/status/{stream_id}` - Get stream status
- `GET /api/camera/hls/playlist/{stream_id}/playlist.m3u8` - HLS manifest

## Troubleshooting

### Backend Issues

**"Failed to fetch" error:**
1. Make sure backend is running: `http://localhost:8000/health`
2. Check if port 8000 is available
3. Verify CORS settings in `app/main.py`

**Camera connection fails:**
1. Verify camera URL is correct
2. Check if camera is on the same network
3. Test camera URL in browser first
4. Check firewall settings

**HLS streaming not working:**
1. Ensure ffmpeg is installed: `ffmpeg -version`
2. Check HLS output directory exists: `backend/static/hls`
3. Verify camera URL returns valid video/image

### Frontend Issues

**HLS player not loading:**
1. Check browser console for errors
2. Verify HLS.js is installed: `npm list hls.js`
3. Try a different browser (Chrome/Firefox recommended)

**CORS errors:**
1. Backend must be running on `http://localhost:8000`
2. Frontend must be on `http://localhost:3000`
3. Check CORS settings in backend

## Dependencies

### Backend
- Python 3.8+
- aiohttp
- fastapi
- uvicorn
- ffmpeg-python
- opencv-python-headless
- numpy

### Frontend
- React 19+
- hls.js
- react-router-dom

## Configuration

### Camera Settings (`backend/config/config.yaml`)
```yaml
camera:
  default_url: "http://192.168.1.6:8080"
  timeout: 10.0
  verify_ssl: false
```

### HLS Settings
```yaml
hls:
  output_dir: "static/hls"
  segment_duration: 4
  window_size: 6
  variants:
    - width: 1280
      height: 720
      bitrate: "2000k"
```

## Network Setup

### Same Network
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Camera: `http://192.168.1.6:8080`

### Different Network
Update CORS in `backend/app/main.py`:
```python
origins = [
    "http://your-frontend-ip:3000",
]
```

## Support

For issues:
1. Check backend logs in terminal
2. Check browser console (F12)
3. Verify all services are running
4. Test endpoints individually

## Quick Health Check

```bash
# Test backend
curl http://localhost:8000/health

# Test camera connection
curl "http://localhost:8000/api/camera/test-connection?camera_url=http://192.168.1.6:8080"

# Check frontend
curl http://localhost:3000
```
