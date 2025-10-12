# app/camera/config.py

from pathlib import Path
from typing import List, Dict, Any
from ..core.config import get_config_value

class CameraConfig:
    """Camera configuration settings"""
    
    def __init__(self):
        self.url: str = get_config_value("camera.default_url")
        self.timeout: float = get_config_value("camera.timeout", 5.0)
        self.verify_ssl: bool = get_config_value("camera.verify_ssl", False)
        self.user_agent: str = get_config_value(
            "camera.user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
         # Add default_url as an alias for url for backward compatibility
        self.default_url = self.url

class HLSConfig:
    """HLS streaming configuration"""
    
    def __init__(self):
        self.output_dir: str = get_config_value("hls.output_dir", "static/hls")
        self.variants: List[Dict[str, Any]] = get_config_value(
            "hls.variants",
            [
                {"width": 1280, "height": 720, "bitrate": "2000k"},
                {"width": 854, "height": 480, "bitrate": "1000k"},
                {"width": 640, "height": 360, "bitrate": "500k"}
            ]
        )
        self.segment_duration: int = get_config_value("hls.segment_duration", 4)
        self.window_size: int = get_config_value("hls.window_size", 6)
        self.cleanup_interval: int = get_config_value("hls.cleanup_interval", 60)
        self.stream_timeout: int = get_config_value("hls.stream_timeout", 3600)

class MLConfig:
    """Machine Learning configuration"""
    
    def __init__(self):
        self.default_model: str = get_config_value("ml.default_model", "csrnet")
        self.models: Dict[str, bool] = {
            "csrnet": get_config_value("ml.models.csrnet.enabled", True),
            "tmtb": get_config_value("ml.models.tmtb.enabled", True)
        }

# Create singleton instances
camera_config = CameraConfig()
hls_config = HLSConfig()
ml_config = MLConfig()