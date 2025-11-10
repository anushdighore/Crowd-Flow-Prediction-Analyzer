# Deployment Guide

Complete guide for deploying the Multi-Model Crowd Counting System to production.

## Deployment Options

### 1. Local/Development Server

**Use case**: Development, testing, local demonstrations

```bash
cd backend
python run.py
```

Runs on `http://localhost:8000`

### 2. Docker Container

**Use case**: Consistent environment, easy scaling, cloud deployment

**Build Image:**

```bash
docker build -t crowd-counting:latest .
```

**Run Container:**

```bash
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/models:/app/models \
  --name crowd-api \
  crowd-counting:latest
```

**Docker Compose:**

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./models:/app/models
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - GPU_MEMORY_FRACTION=0.8
    gpu:
      count: 1
      capabilities: [compute, utility]

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### 3. Cloud Deployment

#### AWS (EC2 + ECS)

**EC2 Instance Setup:**

```bash
# Use GPU-enabled instance (p3, g4dn family)
# Deep Learning AMI with NVIDIA CUDA pre-installed

# SSH into instance
ssh -i key.pem ubuntu@instance-ip

# Clone repository
git clone <repo>
cd crowd-counting

# Install dependencies
pip install -r requirements.txt

# Start backend
python backend/run.py
```

**ECS Deployment:**

```bash
# Create ECR repository
aws ecr create-repository --repository-name crowd-counting

# Build and push image
docker build -t crowd-counting:latest .
docker tag crowd-counting:latest $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/crowd-counting:latest
docker push $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/crowd-counting:latest

# Create ECS task definition with GPU support
# Deploy to ECS cluster
```

#### Google Cloud (Vertex AI)

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/$PROJECT_ID/crowd-counting

# Deploy to Vertex AI
gcloud ai models upload \
  --region=us-central1 \
  --display-name=crowd-counting \
  --container-image-uri=gcr.io/$PROJECT_ID/crowd-counting
```

#### Azure (Container Instances)

```bash
# Push to Azure Container Registry
az acr build --registry <registry-name> -t crowd-counting:latest .

# Deploy container instance
az container create \
  --resource-group <group> \
  --name crowd-api \
  --image <registry>.azurecr.io/crowd-counting:latest \
  --gpu 1 \
  --ports 8000 \
  --environment-variables \
    API_PORT=8000 \
    GPU_MEMORY_FRACTION=0.8
```

### 4. Kubernetes Deployment

**Helm Chart:**

```bash
cd helm
helm install crowd-counting ./crowd-counting \
  --set image.tag=latest \
  --set replicas=3 \
  --set gpu.enabled=true \
  --set gpu.count=1
```

**Kubernetes Manifest:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: crowd-api
spec:
  selector:
    app: crowd-api
  ports:
    - port: 8000
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crowd-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: crowd-api
  template:
    metadata:
      labels:
        app: crowd-api
    spec:
      containers:
        - name: crowd-api
          image: crowd-counting:latest
          ports:
            - containerPort: 8000
          resources:
            requests:
              nvidia.com/gpu: 1
              memory: "8Gi"
              cpu: "4"
            limits:
              nvidia.com/gpu: 1
              memory: "16Gi"
              cpu: "8"
          volumeMounts:
            - name: models
              mountPath: /app/models
      volumes:
        - name: models
          persistentVolumeClaim:
            claimName: models-pvc
```

## Production Configuration

### config/config.yaml

```yaml
app:
  name: "Crowd Counting API"
  version: "1.0.0"
  debug: false # Disable debug mode in production
  log_level: "INFO"

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false

models:
  csrnet:
    enabled: true
    weights: "/models/csrnet_final.pth"
    device: "cuda:0"
  tmtb:
    enabled: true
    weights: "/models/tmtb_final.pth"
    device: "cuda:0"

inference:
  batch_size: 1
  max_workers: 4
  gpu_memory_fraction: 0.8
  timeout_seconds: 30

api:
  cors_origins: ["https://yourdomain.com"]
  rate_limit: 100 # requests per minute
  max_file_size_mb: 50

security:
  api_key_required: true # Enable API key validation
  ssl_enabled: true
  ssl_cert: "/etc/ssl/certs/server.crt"
  ssl_key: "/etc/ssl/private/server.key"
```

### Security Setup

**Enable HTTPS:**

```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Use Let's Encrypt (production)
certbot certonly --standalone -d yourdomain.com
```

**API Key Authentication:**

```bash
# Generate API keys
python scripts/generate_api_keys.py

# Use in requests
curl -H "X-API-Key: your-key" http://api.domain.com/api/v1/predict
```

**CORS Configuration:**

```python
# In main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Optimization

### Load Balancing

**Nginx Configuration:**

```nginx
upstream crowd_api {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://crowd_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Caching

Enable Redis caching for identical requests:

```python
# In backend/app/cache.py
from redis import Redis

cache = Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.post("/api/v1/csrnet/predict")
async def predict(request: PredictionRequest):
    cache_key = f"prediction:{request.image_url}"

    # Check cache
    if cache_key in cache:
        return json.loads(cache[cache_key])

    # Run inference
    result = await run_inference(request)

    # Store in cache (1 hour TTL)
    cache.setex(cache_key, 3600, json.dumps(result))

    return result
```

### Database Setup (Optional)

For result persistence:

```python
# PostgreSQL with SQLAlchemy
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@db:5432/crowd_counting"
engine = create_engine(DATABASE_URL)

# Store results
@app.post("/api/v1/predict")
async def predict(request: PredictionRequest, db: Session = Depends()):
    result = await inference(request)

    # Save to database
    db_result = PredictionResult(
        image_url=request.image_url,
        csrnet_count=result.csrnet_count,
        tmtb_count=result.tmtb_count,
        timestamp=datetime.now()
    )
    db.add(db_result)
    db.commit()

    return result
```

## Monitoring & Logging

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

predictions_total = Counter(
    'predictions_total',
    'Total predictions',
    ['model']
)

prediction_duration = Histogram(
    'prediction_duration_seconds',
    'Prediction duration',
    ['model']
)

@app.post("/api/v1/predict")
async def predict(request: PredictionRequest):
    with prediction_duration.labels(model='csrnet').time():
        result = await run_inference(request)
        predictions_total.labels(model='csrnet').inc()
    return result
```

### Logging Configuration

```python
import logging
from pythonjsonlogger import jsonlogger

handler = logging.FileHandler('/var/log/crowd-api/app.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Log Aggregation (ELK Stack)

```yaml
# docker-compose.yml additions
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

## Backup & Recovery

### Model Checkpoints

```bash
# Regular backups to S3
aws s3 sync ./models s3://backup-bucket/models --delete

# Automated backup schedule
0 2 * * * aws s3 sync /app/models s3://backup-bucket/models --delete
```

### Database Backups

```bash
# PostgreSQL backup
pg_dump -h db-host -U postgres crowd_counting > backup.sql

# Restore
psql -h db-host -U postgres crowd_counting < backup.sql
```

## Scaling Strategies

### Horizontal Scaling

Deploy multiple backend instances behind load balancer:

```
Client → Load Balancer → [Backend 1, Backend 2, Backend 3]
                         └─ Shared Model Cache (Redis)
                         └─ Shared Database
```

### Vertical Scaling

Increase GPU memory and batch size:

```yaml
inference:
  batch_size: 4 # Process 4 images simultaneously
  max_workers: 8 # More concurrent workers
```

## Troubleshooting

### GPU Out of Memory

```bash
# Reduce batch size
batch_size: 1

# Enable mixed precision
mixed_precision: true

# Limit GPU memory
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=1
```

### Slow Response Times

```bash
# Check GPU utilization
nvidia-smi

# Check CPU usage
top -p $(pgrep -f "python run.py")

# Profile with py-spy
py-spy record -o profile.svg python run.py
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port in config
server:
  port: 8001
```

## CI/CD Pipeline

### GitHub Actions

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t crowd-counting:${{ github.sha }} .

      - name: Push to ECR
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          aws ecr get-login-password --region us-east-1 | \
          docker login --username AWS --password-stdin $ECR_REGISTRY
          docker push $ECR_REGISTRY/crowd-counting:${{ github.sha }}

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster production \
            --service crowd-api \
            --force-new-deployment
```

## Health Checks

### Liveness Probe

```python
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}
```

### Readiness Probe

```python
@app.get("/health/ready")
async def readiness():
    # Check model loaded
    if not models_loaded:
        raise HTTPException(status_code=503)
    return {"status": "ready"}
```

## Rollback Procedures

```bash
# Rollback to previous version
docker pull crowd-counting:previous
docker stop crowd-api
docker rm crowd-api
docker run -d --name crowd-api crowd-counting:previous

# Or with Kubernetes
kubectl rollout undo deployment/crowd-api
```

## Support & Maintenance

- Monitor error logs daily
- Update dependencies monthly
- Test backup/recovery quarterly
- Review performance metrics weekly
- Update model weights periodically

---

**Last Updated**: 2024  
**Status**: Production Ready  
**Supported Platforms**: AWS, GCP, Azure, On-Premise, Kubernetes
