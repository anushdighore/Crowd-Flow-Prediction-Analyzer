# Backend Cache Management

## 📦 Cache Directory Structure

All cache files are now consolidated in the `target/` directory:

```
backend/
├── target/
│   ├── pycache/           # Python bytecode cache (__pycache__)
│   ├── .pytest_cache/     # Pytest cache
│   ├── coverage/          # Test coverage reports
│   └── *.egg-info/        # Package metadata
```

## ⚙️ Configuration

### 1. **Python Bytecode Cache**

- **Location**: `target/pycache/`
- **Set via**: `PYTHONPYCACHEPREFIX` environment variable
- **Configured in**: `.env`, `start_backend.bat`, `start_backend.sh`

### 2. **Pytest Cache**

- **Location**: `target/.pytest_cache/`
- **Configured in**: `pytest.ini`, `pyproject.toml`

### 3. **Git Ignore**

- All cache directories are ignored in `.gitignore`
- The `target/` directory is fully excluded from version control

## 🚀 Usage

### Start Backend (with proper cache settings):

```bash
# Windows
start_backend.bat

# Linux/Mac
./start_backend.sh
```

### Cleanup Old Cache Files:

```bash
# Windows
scripts\cleanup_cache.bat

# Linux/Mac
./scripts/cleanup_cache.sh
```

### Run Tests (cache goes to target/):

```bash
pytest  # Automatically uses target/.pytest_cache
```

## 🛠️ Manual Configuration

### Set environment variable manually:

**Windows (CMD):**

```cmd
set PYTHONPYCACHEPREFIX=target/pycache
python app/main.py
```

**Windows (PowerShell):**

```powershell
$env:PYTHONPYCACHEPREFIX="target/pycache"
python app/main.py
```

**Linux/Mac:**

```bash
export PYTHONPYCACHEPREFIX=target/pycache
python app/main.py
```

## ✅ Benefits

1. **Clean workspace**: No more `__pycache__` folders scattered everywhere
2. **Easy cleanup**: Just delete `target/` to remove all cache
3. **Better git**: Cleaner `git status` output
4. **Organized**: All build artifacts in one place
5. **CI/CD friendly**: Easy to cache/restore in pipelines

## 📝 Notes

- The `target/` directory is auto-created if it doesn't exist
- Cache files are safe to delete anytime
- Changes take effect immediately after setting `PYTHONPYCACHEPREFIX`
