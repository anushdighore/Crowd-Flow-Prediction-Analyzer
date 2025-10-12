"""
Config Loader - Type-safe YAML configuration loader with Pydantic validation

Loads model-specific configuration from YAML files with caching for performance.
Follows industry best practices from Google Vision API and TensorFlow.
"""
import yaml
from pathlib import Path
from typing import Dict, Optional
from functools import lru_cache
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models for Type-Safe Configuration
# ============================================================================

class DimensionConfig(BaseModel):
    """Image dimensions for a specific source"""
    length: int = Field(gt=0, description="Width in pixels")
    breadth: int = Field(gt=0, description="Height in pixels")
    
    @validator('length', 'breadth')
    def validate_dimensions(cls, v):
        """Ensure dimensions are reasonable (32-4096 pixels)"""
        if not (32 <= v <= 4096):
            raise ValueError(f"Dimension must be between 32 and 4096, got {v}")
        return v


class NormalizeConfig(BaseModel):
    """Normalization parameters (ImageNet defaults)"""
    mean: list[float] = [0.485, 0.456, 0.406]
    std: list[float] = [0.229, 0.224, 0.225]
    
    @validator('mean', 'std')
    def validate_length(cls, v):
        """Ensure 3 values for RGB channels"""
        if len(v) != 3:
            raise ValueError(f"Must have 3 values for RGB channels, got {len(v)}")
        return v


class PreprocessingConfig(BaseModel):
    """Preprocessing configuration for different input sources"""
    image: DimensionConfig
    webcam: DimensionConfig
    video: DimensionConfig
    surveillance: DimensionConfig
    normalize: NormalizeConfig
    resize_mode: str = "bilinear"
    
    def get_dimensions(self, source: str) -> DimensionConfig:
        """Get dimensions for a specific source
        
        Args:
            source: One of 'image', 'webcam', 'video', 'surveillance'
            
        Returns:
            DimensionConfig with length and breadth
            
        Raises:
            ValueError: If source is not recognized
        """
        source_lower = source.lower()
        
        # Map 'upload' to 'image' for backwards compatibility
        if source_lower == 'upload':
            source_lower = 'image'
        
        if hasattr(self, source_lower):
            return getattr(self, source_lower)
        else:
            raise ValueError(
                f"Unknown source '{source}'. Must be one of: "
                f"image, webcam, video, surveillance (or 'upload' as alias for 'image')"
            )


class ModelArchitectureConfig(BaseModel):
    """Model architecture parameters"""
    pass  # Flexible - different models have different fields


class ModelConfig(BaseModel):
    """Model metadata"""
    name: str
    checkpoint: str
    architecture: Optional[Dict] = None


class InferenceConfig(BaseModel):
    """Inference settings"""
    precision: str = "fp32"
    batch_size: int = 1
    warmup: bool = True
    warmup_iterations: int = 3
    requires_grad: bool = False


class OptimizationConfig(BaseModel):
    """Performance optimization settings"""
    compile_model: bool = False
    compile_mode: str = "default"
    channels_last: bool = False
    cudnn_benchmark: bool = True


class CacheConfig(BaseModel):
    """Caching configuration"""
    cache_model: bool = True
    cache_preprocessing: bool = False
    cache_results: bool = False


class LoggingConfig(BaseModel):
    """Logging configuration"""
    log_inference_time: bool = True
    log_memory: bool = True
    log_output_stats: bool = False


# ============================================================================
# Model-Specific Configuration Classes
# ============================================================================

class CSRNetConfig(BaseModel):
    """Complete CSRNet configuration"""
    model: ModelConfig
    preprocessing: PreprocessingConfig
    inference: Optional[InferenceConfig] = None
    optimization: Optional[OptimizationConfig] = None
    cache: Optional[CacheConfig] = None
    logging: Optional[LoggingConfig] = None


class TMTBConfig(BaseModel):
    """Complete TMTB configuration"""
    model: ModelConfig
    preprocessing: PreprocessingConfig
    inference: Optional[InferenceConfig] = None
    optimization: Optional[OptimizationConfig] = None
    cache: Optional[CacheConfig] = None
    logging: Optional[LoggingConfig] = None


# ============================================================================
# Config Loading Functions (with @lru_cache for performance)
# ============================================================================

def _get_config_path(model_name: str) -> Path:
    """Get path to config file for a model
    
    Args:
        model_name: 'csrnet' or 'tmtb'
        
    Returns:
        Path to config file
    """
    # Get ml/config directory (assumes this file is in ml/src/core/)
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_file = config_dir / f"{model_name}_config.yaml"
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    return config_file


@lru_cache(maxsize=8)
def load_csrnet_config(config_path: Optional[str] = None) -> CSRNetConfig:
    """Load CSRNet configuration from YAML file
    
    Uses @lru_cache for performance - config is loaded once and cached.
    
    Args:
        config_path: Optional custom path to config file
        
    Returns:
        CSRNetConfig with validated configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValidationError: If config validation fails
    """
    if config_path is None:
        config_path = _get_config_path("csrnet")
    else:
        config_path = Path(config_path)
    
    logger.info(f"Loading CSRNet config from: {config_path}")
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    config = CSRNetConfig(**config_dict)
    logger.debug(f"CSRNet config loaded successfully")
    
    return config


@lru_cache(maxsize=8)
def load_tmtb_config(config_path: Optional[str] = None) -> TMTBConfig:
    """Load TMTB configuration from YAML file
    
    Uses @lru_cache for performance - config is loaded once and cached.
    
    Args:
        config_path: Optional custom path to config file
        
    Returns:
        TMTBConfig with validated configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValidationError: If config validation fails
    """
    if config_path is None:
        config_path = _get_config_path("tmtb")
    else:
        config_path = Path(config_path)
    
    logger.info(f"Loading TMTB config from: {config_path}")
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    config = TMTBConfig(**config_dict)
    logger.debug(f"TMTB config loaded successfully")
    
    return config


def clear_config_cache():
    """Clear config cache (useful for hot-reloading during development)"""
    load_csrnet_config.cache_clear()
    load_tmtb_config.cache_clear()
    logger.info("Config cache cleared")


# ============================================================================
# Convenience Functions
# ============================================================================

def get_dimensions_for_source(model: str, source: str) -> DimensionConfig:
    """Get dimensions for a specific model and source
    
    Args:
        model: 'csrnet' or 'tmtb'
        source: 'image', 'webcam', 'video', 'surveillance' (or 'upload' as alias)
        
    Returns:
        DimensionConfig with length and breadth
        
    Example:
        >>> dims = get_dimensions_for_source('csrnet', 'webcam')
        >>> print(dims.length, dims.breadth)  # 640, 640
    """
    if model.lower() == 'csrnet':
        config = load_csrnet_config()
    elif model.lower() == 'tmtb':
        config = load_tmtb_config()
    else:
        raise ValueError(f"Unknown model '{model}'. Must be 'csrnet' or 'tmtb'")
    
    return config.preprocessing.get_dimensions(source)
