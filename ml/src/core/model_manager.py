"""
Model Manager - Load, cache, and manage ML models

Handles:
- Model loading from checkpoints
- Device placement
- Model caching
- Warmup inference
- Multi-model support

Works with DeviceManager for optimal device placement
"""

import torch
import torch.nn as nn
import logging
from typing import Dict, Optional, Any
from pathlib import Path
import time
import yaml

from .device_manager import DeviceManager, get_device_manager

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model loading, caching, and lifecycle"""
    
    def __init__(
        self,
        device_manager: Optional[DeviceManager] = None,
        config_dir: Optional[Path] = None
    ):
        """
        Initialize ModelManager
        
        Args:
            device_manager: DeviceManager instance (optional, will create if None)
            config_dir: Directory containing model configs
        """
        self.device_manager = device_manager or get_device_manager()
        self.config_dir = config_dir or (Path(__file__).parent.parent.parent / "config")
        
        # Model cache: {model_name: model_instance}
        self.models: Dict[str, nn.Module] = {}
        
        # Model configs: {model_name: config_dict}
        self.configs: Dict[str, Dict[str, Any]] = {}
        
        # Model metadata: {model_name: {device, checkpoint_path, load_time, etc.}}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Model Manager initialized")
    
    def load_model(
        self,
        model_name: str,
        checkpoint_path: Optional[str] = None,
        device: Optional[str] = None,
        force_reload: bool = False
    ) -> nn.Module:
        """
        Load model from checkpoint
        
        Args:
            model_name: Model identifier ('csrnet', 'tmtb', etc.)
            checkpoint_path: Path to checkpoint file (None = use config)
            device: Target device (None = use DeviceManager best device)
            force_reload: Force reload even if cached
            
        Returns:
            Loaded model instance
        """
        # Check cache
        if model_name in self.models and not force_reload:
            logger.info(f"Using cached model: {model_name}")
            return self.models[model_name]
        
        # Load config
        config = self._load_model_config(model_name)
        self.configs[model_name] = config
        
        # Determine checkpoint path
        if checkpoint_path is None:
            checkpoint_path = config['model']['checkpoint']
        
        # Resolve relative path
        checkpoint_path = self._resolve_path(checkpoint_path)
        
        if not Path(checkpoint_path).exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        # Determine device
        if device is None:
            device = self.device_manager.current_device
        
        # Check VRAM before loading (if GPU)
        if device == 'cuda':
            vram_info = self.device_manager.get_vram_usage()
            if vram_info:
                logger.info(f"VRAM before load: {vram_info['free_mb']:.0f}MB free")
        
        # Load model
        logger.info(f"Loading {model_name} from {checkpoint_path} to {device}")
        start_time = time.time()
        
        try:
            model = self._load_model_architecture(model_name, checkpoint_path, device, config)
            load_time = time.time() - start_time
            
            # Cache model
            self.models[model_name] = model
            
            # Store metadata
            self.metadata[model_name] = {
                'checkpoint_path': checkpoint_path,
                'device': device,
                'load_time': load_time,
                'parameters': sum(p.numel() for p in model.parameters()),
            }
            
            logger.info(f"✅ {model_name} loaded in {load_time:.2f}s")
            logger.info(f"   Parameters: {self.metadata[model_name]['parameters']:,}")
            
            # Check VRAM after loading
            if device == 'cuda':
                vram_info = self.device_manager.get_vram_usage()
                if vram_info:
                    logger.info(f"   VRAM after load: {vram_info['allocated_mb']:.0f}MB used, "
                              f"{vram_info['free_mb']:.0f}MB free")
            
            # Warmup if enabled
            if config['inference']['warmup']:
                self.warmup_model(model_name)
            
            return model
        
        except Exception as e:
            logger.error(f"Failed to load {model_name}: {e}")
            raise
    
    def _load_model_config(self, model_name: str) -> Dict[str, Any]:
        """Load model configuration from YAML"""
        config_path = self.config_dir / f"{model_name}_config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded config for {model_name}")
        return config
    
    def _resolve_path(self, path: str) -> str:
        """Resolve path relative to project root"""
        path_obj = Path(path)
        
        if path_obj.is_absolute():
            return str(path_obj)
        
        # Resolve relative to project root (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent.parent
        resolved = project_root / path
        
        return str(resolved)
    
    def _load_model_architecture(
        self,
        model_name: str,
        checkpoint_path: str,
        device: str,
        config: Dict[str, Any]
    ) -> nn.Module:
        """
        Load model architecture and weights
        
        This method dispatches to model-specific loaders
        """
        if model_name == 'csrnet':
            return self._load_csrnet(checkpoint_path, device, config)
        elif model_name == 'tmtb':
            return self._load_tmtb(checkpoint_path, device, config)
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    def _load_csrnet(
        self,
        checkpoint_path: str,
        device: str,
        config: Dict[str, Any]
    ) -> nn.Module:
        """Load CSRNet model"""
        # Import here to avoid circular dependency
        from models.csrnet.csrnet import load_csrnet
        
        model = load_csrnet(checkpoint_path, device=device)
        return model
    
    def _load_tmtb(
        self,
        checkpoint_path: str,
        device: str,
        config: Dict[str, Any]
    ) -> nn.Module:
        """Load TMTB model (placeholder)"""
        raise NotImplementedError("TMTB loading will be implemented later")
    
    def get_model(self, model_name: str) -> Optional[nn.Module]:
        """
        Get cached model
        
        Args:
            model_name: Model identifier
            
        Returns:
            Model instance or None if not loaded
        """
        return self.models.get(model_name)
    
    def warmup_model(self, model_name: str):
        """
        Warmup model with dummy inputs
        
        Args:
            model_name: Model identifier
        """
        model = self.get_model(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not loaded")
        
        config = self.configs[model_name]
        device = self.metadata[model_name]['device']
        iterations = config['inference']['warmup_iterations']
        
        logger.info(f"Warming up {model_name} ({iterations} iterations)...")
        
        # Create dummy input
        dummy_input = torch.randn(1, 3, 480, 640).to(device)
        
        # Warmup
        model.eval()
        with torch.no_grad():
            for i in range(iterations):
                _ = model(dummy_input)
                if device == 'cuda':
                    torch.cuda.synchronize()
        
        logger.info(f"✅ {model_name} warmup complete")
    
    def unload_model(self, model_name: str):
        """
        Unload model from memory
        
        Args:
            model_name: Model identifier
        """
        if model_name in self.models:
            del self.models[model_name]
            if model_name in self.metadata:
                del self.metadata[model_name]
            if model_name in self.configs:
                del self.configs[model_name]
            
            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info(f"Unloaded model: {model_name}")
        else:
            logger.warning(f"Model {model_name} not found in cache")
    
    def switch_device(self, model_name: str, new_device: str):
        """
        Move model to different device
        
        Args:
            model_name: Model identifier
            new_device: Target device
        """
        model = self.get_model(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not loaded")
        
        logger.info(f"Moving {model_name} to {new_device}")
        
        model.to(new_device)
        self.metadata[model_name]['device'] = new_device
        
        logger.info(f"✅ {model_name} moved to {new_device}")
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model metadata
        
        Args:
            model_name: Model identifier
            
        Returns:
            Model metadata or None if not loaded
        """
        return self.metadata.get(model_name)
    
    def list_loaded_models(self) -> list:
        """Get list of loaded model names"""
        return list(self.models.keys())


# Singleton instance
_model_manager_instance: Optional[ModelManager] = None


def get_model_manager(
    device_manager: Optional[DeviceManager] = None,
    config_dir: Optional[Path] = None
) -> ModelManager:
    """
    Get singleton ModelManager instance
    
    Args:
        device_manager: DeviceManager instance (only used on first call)
        config_dir: Config directory (only used on first call)
        
    Returns:
        ModelManager instance
    """
    global _model_manager_instance
    
    if _model_manager_instance is None:
        _model_manager_instance = ModelManager(device_manager, config_dir)
    
    return _model_manager_instance
