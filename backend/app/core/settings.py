"""
Settings configuration using Pydantic
Loads from .env file and provides type-safe access to configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Crowd Counter API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Paths (relative to backend root)
    backend_root: Path = Path(__file__).parent.parent.parent
    config_dir: Path = backend_root / "config"
    ml_root: Path = backend_root.parent / "ml"
    checkpoints_dir: Path = ml_root / "checkpoints"
    
    # Model Configuration
    default_model: str = "csrnet"
    device: str = "cuda"  # or "cpu"
    
    # Logging
    log_level: str = "INFO"
    
    # Cache
    cache_dir: Path = backend_root / "target" / "pycache"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Allow reading from environment with prefix
        # e.g., CROWD_API_PORT instead of API_PORT
        env_prefix = ""


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance
    Use this function to get settings throughout the app
    """
    return Settings()


# Convenience access
settings = get_settings()
