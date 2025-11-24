# Troubleshooting: Upload Image Page Not Working

## Problem

The Upload Image page (YOLOUploader) is not working and showing "failed" error.

## Quick Fixes

### Fix 1: Check if Backend is Running

1. Open a terminal/cmd
2. Navigate to backend:
   ```bash
   cd "d:\College\Major Project\backend"
   ```
3. Start the backend:
   ```bash
   python run.py
   ```
4. Look for: `✅ Available models` or `Uvicorn running on http://0.0.0.0:8000`

### Fix 2: Check Backend API Endpoint

Open browser and visit:

```
http://localhost:8000/api/v1/yolo/health
```

**Expected Response:**

```json
{
  "status": "ok",
  "model": "YOLOv8",
  "description": "YOLOv8-based object detection for crowd counting",
  "approach": "Object Detection"
}
```

**If you get error:** Backend is not running or endpoint is broken.

### Fix 3: Test API Endpoint Directly

Open browser and visit:

```
http://localhost:8000/docs
```

This will open FastAPI Swagger UI. Look for `/api/v1/yolo/detect` endpoint and test it.

### Fix 4: Check CORS Settings

The backend needs to allow requests from frontend. Check `backend/app/main.py`:

```python
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    ...
]
```

Make sure your frontend URL is in the list.

### Fix 5: Check Frontend Console

1. Open Upload Image page
2. Press F12 (Developer Tools)
3. Go to Console tab
4. Look for errors like:
   - `Failed to fetch` - Backend not running
   - `CORS error` - CORS not configured
   - `404 Not Found` - Wrong endpoint URL
   - `500 Internal Server Error` - Backend crashed

### Fix 6: Verify Frontend API URL

In `YOLOUploader.js`, the API call is:

```javascript
const response = await fetch("http://localhost:8000/api/v1/yolo/detect", {
  method: "POST",
  body: formData,
});
```

Make sure:

- Backend is running on port 8000
- Endpoint path is correct: `/api/v1/yolo/detect`

## Common Errors and Solutions

### Error: "Failed to fetch"

**Cause:** Backend not running or wrong URL
**Solution:**

1. Start backend: `cd backend && python run.py`
2. Verify URL in YOLOUploader.js matches backend port

### Error: "CORS policy blocked"

**Cause:** Frontend origin not allowed
**Solution:** Add frontend URL to CORS origins in `backend/app/main.py`

### Error: "404 Not Found"

**Cause:** Endpoint doesn't exist or wrong path
**Solution:**

1. Check `backend/app/main.py` includes yolo router:
   ```python
   app.include_router(yolo_router, prefix="/api/v1", tags=["yolo"])
   ```
2. Verify endpoint URL is correct

### Error: "500 Internal Server Error"

**Cause:** Backend crashed during processing
**Solution:**

1. Check backend console for error stack trace
2. Common causes:
   - YOLO model file missing (`yolov8n.pt`)
   - Import error (models not found)
   - PIL/numpy version incompatibility

### Error: Component not rendering

**Cause:** React error or missing import
**Solution:**

1. Check browser console (F12)
2. Look for red errors
3. Common causes:
   - Component import path wrong
   - Syntax error in JSX
   - Missing dependency

## Testing Steps

### Step 1: Start Backend

```bash
cd "d:\College\Major Project\backend"
python run.py
```

Wait for:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Available models: ['yolo', 'csrnet', ...]
```

### Step 2: Start Frontend

```bash
cd "d:\College\Major Project\frontend"
npm start
```

Wait for:

```
Compiled successfully!
webpack compiled with 0 warnings
```

### Step 3: Test Upload

1. Go to: `http://localhost:3000`
2. Click "Upload Image" button
3. Select YOLO model
4. Click file upload area
5. Select an image with people
6. Click "Analyze with YOLO"
7. Watch for results

### Step 4: Check Logs

**Backend logs:**

- Check terminal where backend is running
- Look for errors during image processing

**Frontend logs:**

- Open browser console (F12)
- Look for network errors or JavaScript errors

## Advanced Debugging

### Check Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Upload an image
4. Look for `/api/v1/yolo/detect` request
5. Click on it to see:
   - Request headers
   - Request payload (image file)
   - Response status code
   - Response body

### Check If Model File Exists

```bash
cd "d:\College\Major Project\backend"
dir yolov8n.pt
```

If file doesn't exist, YOLO won't work. Download from:
https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

### Test with cURL (Windows PowerShell)

```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/yolo/health -Method GET
```

Should return JSON with status "ok".

## Still Not Working?

If none of the above fixes work:

1. **Restart everything:**

   - Close all terminals
   - Stop backend and frontend
   - Start backend first, then frontend

2. **Clear cache:**

   ```bash
   cd frontend
   npm clean-cache --force
   rm -rf node_modules
   npm install
   ```

3. **Check Python environment:**

   ```bash
   cd backend
   pip list | findstr ultralytics
   pip list | findstr torch
   ```

4. **Reinstall dependencies:**

   ```bash
   cd backend
   pip install -r requirements.txt --upgrade
   ```

5. **Check if port 8000 is in use:**
   ```bash
   netstat -ano | findstr :8000
   ```

## Quick Test Script

Create `test_yolo_api.py` in backend folder:

```python
import requests

# Test health endpoint
response = requests.get("http://localhost:8000/api/v1/yolo/health")
print("Health check:", response.json())

# Test detect endpoint with a file
with open("test_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/v1/yolo/detect", files=files)
    print("Detection result:", response.json())
```

Run:

```bash
cd backend
python test_yolo_api.py
```

## Success Indicators

✅ Backend running: See Uvicorn startup message
✅ Models loaded: See "✅ Available models" log
✅ Health check works: `/api/v1/yolo/health` returns JSON
✅ Frontend loads: Page opens without errors
✅ Upload works: Image can be selected
✅ Analysis works: Results appear after clicking "Analyze"
✅ No console errors: Browser console is clean

## Contact Info

If still stuck, provide:

1. Backend console output (last 20 lines)
2. Frontend console errors (screenshot)
3. Network tab showing failed request
4. Operating system and Python version
5. Node.js version: `node --version`
