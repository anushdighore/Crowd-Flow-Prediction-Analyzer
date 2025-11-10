# Troubleshooting Guide

Solutions for common issues and problems.

## Installation & Setup

### Issue: "ModuleNotFoundError" when importing packages

**Symptom:**

```
ModuleNotFoundError: No module named 'torch'
```

**Solutions:**

```bash
# 1. Verify installation
pip list | grep torch

# 2. Reinstall PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Check Python version matches environment
python --version  # Should be 3.8+

# 4. Verify virtual environment is active
which python  # Should point to venv location
```

### Issue: GPU not detected

**Symptom:**

```python
>>> import torch
>>> torch.cuda.is_available()
False
```

**Solutions:**

```bash
# 1. Check NVIDIA driver
nvidia-smi

# 2. Verify CUDA installation
python -c "import torch; print(torch.version.cuda)"

# 3. Reinstall PyTorch with correct CUDA version
# CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CPU only (as fallback):
pip install torch torchvision torchaudio
```

### Issue: "NumPy version mismatch"

**Symptom:**

```
RuntimeError: module compiled against API version 0x10 but this version of numpy is 0x9
```

**Solutions:**

```bash
# 1. Check NumPy version
python -c "import numpy; print(numpy.__version__)"

# 2. Ensure NumPy < 2.0 for PyTorch compatibility
pip install 'numpy<2'

# 3. Reinstall with specific version
pip install numpy==1.26.4

# 4. Update requirements.txt and reinstall everything
pip install -r requirements.txt --force-reinstall
```

## Backend Server Issues

### Issue: "Address already in use" error

**Symptom:**

```
OSError: [Errno 48] Address already in use
```

**Solutions:**

```bash
# 1. Find process using port 8000
# Linux/Mac:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# 2. Kill process
# Linux/Mac:
kill -9 <PID>

# Windows:
taskkill /PID <PID> /F

# 3. Use different port in config
# Edit config/config.yaml:
server:
  port: 8001

# 4. Use environment variable
export API_PORT=8001
python run.py
```

### Issue: Server crashes on startup

**Symptom:**

```
Traceback (most recent call last):
  File "run.py", line X, in <module>
    ...
RuntimeError: CUDA out of memory
```

**Solutions:**

```bash
# 1. Reduce GPU memory usage in config/config.yaml
inference:
  batch_size: 1
  mixed_precision: true
  gpu_memory_fraction: 0.7

# 2. Use CPU instead (slower but works)
# Edit config:
models:
  csrnet:
    device: "cpu"
  tmtb:
    device: "cpu"

# 3. Clear GPU cache
python -c "import torch; torch.cuda.empty_cache()"

# 4. Check GPU memory
nvidia-smi
```

### Issue: Model loading fails

**Symptom:**

```
FileNotFoundError: [Errno 2] No such file or directory: '/models/csrnet.pth'
```

**Solutions:**

```bash
# 1. Verify model paths
ls -la backend/models/

# 2. Check config paths
cat backend/config/config.yaml | grep weights

# 3. Download models manually
cd backend/models
wget https://link-to-csrnet-weights/csrnet.pth
wget https://link-to-tmtb-weights/tmtb.pth

# 4. Update model paths in config.yaml
models:
  csrnet:
    weights: "/absolute/path/to/csrnet.pth"
```

## API Request Issues

### Issue: 400 Bad Request error

**Symptom:**

```json
{ "error": "Invalid input: image_url is required" }
```

**Solutions:**

```bash
# 1. Check request format
curl -X POST http://localhost:8000/api/v1/csrnet/predict \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'

# 2. Verify URL is valid
# Use valid image URL with .jpg, .png, or .jpeg extension

# 3. Check JSON syntax
# Use jsonlint to validate: jsonlint request.json

# 4. Verify parameters
# Allowed parameters:
# - image_url: string (required)
# - visualize: boolean (optional)
# - return_map: boolean (optional)
```

### Issue: 500 Internal Server Error

**Symptom:**

```json
{ "error": "Internal Server Error" }
```

**Solutions:**

```bash
# 1. Check backend logs
tail -f backend.log

# 2. Verify model weights are corrupted
python -c "import torch; torch.load('path/to/model.pth')"

# 3. Check image format
file image.jpg  # Should show actual format

# 4. Test with simple request
curl http://localhost:8000/health

# 5. Restart backend
# Kill process and restart:
python run.py
```

### Issue: 504 Gateway Timeout

**Symptom:**

```
Request timeout after 30 seconds
```

**Solutions:**

```bash
# 1. Increase timeout in config
inference:
  timeout_seconds: 60

# 2. Reduce image size
# Large images take longer to process
# Max recommended: 1920x1080

# 3. Check GPU utilization
nvidia-smi
# If usage < 50%, backend might be bottlenecked

# 4. Try different endpoint
# VMamba might be faster:
curl -X POST http://localhost:8000/api/v1/tmtb/predict
```

## Image Processing Issues

### Issue: "Image format not supported"

**Symptom:**

```json
{ "error": "Unsupported image format" }
```

**Solutions:**

```bash
# 1. Verify image format
file image.jpg
# Should output: image.jpg: JPEG image data

# 2. Convert image to supported format
# Using ImageMagick:
convert image.bmp image.jpg

# Using ffmpeg:
ffmpeg -i image.png image.jpg

# 3. Check image integrity
python -c "from PIL import Image; Image.open('image.jpg')"

# 4. Download test image
wget https://example.com/valid_image.jpg
```

### Issue: "Image too large" error

**Symptom:**

```json
{ "error": "Image exceeds maximum size" }
```

**Solutions:**

```bash
# 1. Check file size
ls -lh image.jpg
# Should be < 50MB (configurable)

# 2. Reduce image dimensions
# Using ffmpeg:
ffmpeg -i large_image.jpg -vf scale=1920:-1 small_image.jpg

# Using Python:
from PIL import Image
img = Image.open('large.jpg')
img.thumbnail((1920, 1080))
img.save('small.jpg')

# 3. Compress image quality
convert image.jpg -quality 85 compressed.jpg

# 4. Increase size limit in config
api:
  max_file_size_mb: 100
```

### Issue: Poor prediction results

**Symptom:**

```json
{ "count": 999, "confidence": 0.2 }
```

**Solutions:**

```bash
# 1. Check image quality
# Image should be:
# - Well-lit
# - Not blurry
# - At least 640x480 resolution

# 2. Try different model
# VMamba works better on some images:
curl -X POST http://localhost:8000/api/v1/tmtb/predict

# 3. Use ensemble for better results
curl -X POST http://localhost:8000/api/v1/predict

# 4. Check if scene is supported
# Models trained on crowd counting:
# - Indoor/outdoor gatherings
# - Street scenes
# - Event venues
```

## GPU Memory Issues

### Issue: "CUDA out of memory"

**Symptom:**

```
torch.cuda.OutOfMemoryError: CUDA out of memory
```

**Solutions:**

```bash
# 1. Clear GPU cache
python -c "import torch; torch.cuda.empty_cache()"

# 2. Reduce batch size
inference:
  batch_size: 1  # Start with 1

# 3. Enable mixed precision training
training:
  mixed_precision: true

# 4. Move to CPU
models:
  csrnet:
    device: "cpu"  # Slower but uses system RAM

# 5. Check other GPU processes
nvidia-smi
# Kill other processes using GPU
```

### Issue: "Memory leak during inference"

**Symptom:**

```
GPU memory usage keeps increasing
```

**Solutions:**

```python
# 1. Ensure proper cleanup in inference code
import torch

with torch.no_grad():
    output = model(input)
del output, input
torch.cuda.empty_cache()

# 2. Use context managers
with torch.cuda.device(0):
    # Inference code here
    pass

# 3. Monitor memory
import psutil
print(f"GPU: {torch.cuda.memory_allocated()} bytes")
print(f"RAM: {psutil.virtual_memory().percent}%")
```

## Frontend Issues

### Issue: "Connection refused" from frontend

**Symptom:**

```
Error: connect ECONNREFUSED 127.0.0.1:8000
```

**Solutions:**

```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check CORS configuration
# In backend/main.py:
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Check frontend URL
# Verify API_URL in frontend/.env
REACT_APP_API_URL=http://localhost:8000

# 4. Restart both servers
# Kill both processes and restart
```

### Issue: "No image preview in frontend"

**Symptom:**

```
Image shows as broken link
```

**Solutions:**

```bash
# 1. Check base64 encoding
# Verify heatmap field is valid base64

# 2. Verify response includes heatmap
curl -X POST http://localhost:8000/api/v1/csrnet/predict \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg", "visualize": true}'

# 3. Check CORS for image display
# Allow images from API
```

## Performance Issues

### Issue: Slow inference time

**Symptom:**

```
Processing time > 1 second per image
```

**Solutions:**

```bash
# 1. Check GPU utilization
nvidia-smi
# Usage should be 80%+

# 2. Enable mixed precision
training:
  mixed_precision: true

# 3. Optimize image size
# Resize to 640x480
# Smaller images = faster processing

# 4. Use TensorRT for optimization
# (Advanced, requires additional setup)

# 5. Check CPU/GPU ratio
# If CPU < 20%, GPU is bottleneck
# Profile with: nvidia-smi dmon
```

## Logging & Debugging

### Enable Debug Mode

```bash
# Set environment variable
export DEBUG=True
python run.py

# Or in config/config.yaml
app:
  debug: true
  log_level: "DEBUG"
```

### View Logs

```bash
# Real-time logs
tail -f backend.log

# Search for errors
grep "ERROR" backend.log

# Filter by timestamp
grep "2024-01-15" backend.log
```

### Test Individual Components

```bash
# Test PyTorch
python tests/test_models.py

# Test preprocessing
python tests/test_preprocessing.py

# Test API
python -m pytest tests/test_csrnet_api.py -v

# Test camera
python tests/test_camera.py
```

## Common Solutions Checklist

- [ ] Verify Python version (3.8+)
- [ ] Check virtual environment is active
- [ ] Ensure all dependencies installed: `pip install -r requirements.txt`
- [ ] Verify NVIDIA driver: `nvidia-smi`
- [ ] Check PyTorch CUDA support: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Verify model files exist in `backend/models/`
- [ ] Check config.yaml paths are correct
- [ ] Ensure port 8000 is available
- [ ] Clear GPU cache if memory issues: `python -c "import torch; torch.cuda.empty_cache()"`
- [ ] Restart backend server: kill process and restart

## Getting Help

1. Check this guide first
2. Review archived documentation: `docs/archive/`
3. Check API documentation: `docs/API.md`
4. Enable debug logging
5. Collect error logs and system info

---

**Last Updated**: 2024  
**Status**: Comprehensive troubleshooting guide
