# Backend Configuration Guide

## 📁 Configuration File Structure

```
backend/
├── .env                      # ✅ Environment secrets (gitignored)
├── .env.example              # ✅ Template for .env
├── pyproject.toml            # ✅ Python project configuration
├── pytest.ini                # ✅ Pytest configuration
│
├── config/                   # ✅ Application YAML configs
│   ├── config.yaml           # Main application config
│   ├── hyperparams.yaml      # ML hyperparameters
│   └── model_configs/        # Model-specific settings
│
└── app/
    └── core/
        ├── settings.py       # Pydantic settings (loads .env)
        └── config.py         # YAML config loader
```

## 🎯 Configuration Types

### 1. **Environment Variables** (`.env`)

For **secrets** and **environment-specific** settings:

- API keys
- Database URLs
- Debug flags
- Deployment settings

**Example `.env`:**

```env
# Python Cache
PYTHONPYCACHEPREFIX=target/pycache

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Paths
ML_MODELS_PATH=../ml
CHECKPOINTS_PATH=../ml/checkpoints
```

### 2. **YAML Files** (`config/*.yaml`)

For **application logic** and **non-sensitive** settings:

- Model hyperparameters
- Dataset paths
- Image processing settings
- Training configurations

**Example `config/config.yaml`:**

```yaml
data:
  image:
    input_size: [512, 512]
    normalization:
      mean: [0.485, 0.456, 0.406]
      std: [0.229, 0.224, 0.225]

models:
  csrnet:
    checkpoint: "checkpoints/csrnet.pth"
    device: "cuda"
```

### 3. **Python Config** (`pyproject.toml`)

For **package** and **tool** configuration:

- Package metadata
- Dependencies
- Black/isort/pytest settings

---

## 💻 Usage in Code

### Loading Environment Variables:

```python
from app.core.settings import settings

# Access settings (from .env)
print(settings.api_host)        # "0.0.0.0"
print(settings.api_port)        # 8000
print(settings.checkpoints_dir) # Path to checkpoints
```

### Loading YAML Configuration:

```python
from app.core.config import load_config, get_config_value

# Load entire config
config = load_config("config.yaml")
print(config['data']['image']['input_size'])  # [512, 512]

# Get specific value with dot notation
input_size = get_config_value('data.image.input_size')
print(input_size)  # [512, 512]

# With default value
batch_size = get_config_value('training.batch_size', default=32)
```

### Example in FastAPI Endpoint:

```python
from fastapi import APIRouter
from app.core.settings import settings
from app.core.config import get_config_value

router = APIRouter()

@router.get("/config")
async def get_config():
    return {
        "api_version": settings.app_version,
        "model": settings.default_model,
        "input_size": get_config_value('data.image.input_size'),
    }
```

---

## 🔧 Setup Instructions

### 1. Create `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit with your settings
nano .env
```

### 2. Install dependencies:

```bash
pip install pydantic pyyaml python-dotenv
```

### 3. Access in your code:

```python
from app.core.settings import settings
from app.core.config import load_config
```

---

## 🎨 Best Practices

### ✅ **DO:**

- Keep secrets in `.env` (gitignored)
- Use YAML for application logic
- Use Pydantic for type-safe env vars
- Document all config options
- Provide `.env.example` template

### ❌ **DON'T:**

- Commit `.env` to git
- Hardcode secrets in code
- Mix env vars and YAML (choose one per setting)
- Use complex logic in config files

---

## 📝 Config Priority

When the same setting exists in multiple places:

1. **Environment variables** (highest priority)
2. **YAML files**
3. **Default values in code** (lowest priority)

Example:

```python
# 1. Try environment variable
device = os.getenv('DEVICE')

# 2. Try YAML config
if not device:
    device = get_config_value('models.default_device')

# 3. Use default
if not device:
    device = 'cpu'
```

---

## 🚀 Quick Start

```python
# In any file:
from app.core.settings import settings
from app.core.config import get_config_value

# Get env var
port = settings.api_port

# Get YAML config
input_size = get_config_value('data.image.input_size')
```

That's it! Clean, type-safe, and organized configuration management. ✨
