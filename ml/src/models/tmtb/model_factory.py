"""
Model Factory for Multi-Architecture Crowd Counting
Supports: VMamba-TMTB, CSRNet, YOLOv8, and custom models
"""

import logging
import torch
import torch.nn as nn
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelFactory:
    """Factory class to create and manage different crowd counting models"""
    
    SUPPORTED_MODELS = {
        'vmamba_tmtb': {
            'name': 'VMamba-TMTB',
            'description': 'Vision Mamba with Temporal-Multi-scale Token Block',
            'checkpoint': './checkpoints/jhu_5.pth',
            'input_size': (512, 512),
            'requires': ['torch', 'torchvision']
        },
        'csrnet': {
            'name': 'CSRNet',
            'description': 'Congested Scene Recognition Network',
            'checkpoint': './checkpoints/csrnet.pth',
            'input_size': (512, 512),
            'requires': ['torch', 'torchvision']
        },
        'yolov8': {
            'name': 'YOLOv8',
            'description': 'YOLOv8 Object Detection for Crowd Counting',
            'checkpoint': './checkpoints/yolov8n.pt',
            'input_size': (640, 640),
            'requires': ['ultralytics']
        },
        'mcnn': {
            'name': 'MCNN',
            'description': 'Multi-Column CNN for Crowd Counting',
            'checkpoint': './checkpoints/mcnn.pth',
            'input_size': (512, 512),
            'requires': ['torch', 'torchvision']
        }
    }
    
    @staticmethod
    def create_model(
        model_type: str,
        checkpoint_path: Optional[str] = None,
        device: str = 'cuda',
        **kwargs
    ) -> nn.Module:
        """
        Create and load a crowd counting model
        
        Args:
            model_type: Type of model ('vmamba_tmtb', 'csrnet', 'yolov8', 'mcnn')
            checkpoint_path: Path to model checkpoint (optional)
            device: Device to load model on ('cuda' or 'cpu')
            **kwargs: Additional model-specific parameters
            
        Returns:
            Loaded model ready for inference
        """
        model_type = model_type.lower()
        
        if model_type not in ModelFactory.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model type: {model_type}. "
                f"Supported models: {list(ModelFactory.SUPPORTED_MODELS.keys())}"
            )
        
        model_info = ModelFactory.SUPPORTED_MODELS[model_type]
        checkpoint = checkpoint_path or model_info['checkpoint']
        
        logger.info(f"🔧 Creating {model_info['name']} model...")
        logger.info(f"📂 Checkpoint: {checkpoint}")
        
        try:
            if model_type == 'vmamba_tmtb':
                model = ModelFactory._create_vmamba_tmtb(checkpoint, device, **kwargs)
            elif model_type == 'csrnet':
                model = ModelFactory._create_csrnet(checkpoint, device, **kwargs)
            elif model_type == 'yolov8':
                model = ModelFactory._create_yolov8(checkpoint, device, **kwargs)
            elif model_type == 'mcnn':
                model = ModelFactory._create_mcnn(checkpoint, device, **kwargs)
            else:
                raise ValueError(f"Model type {model_type} not implemented")
            
            logger.info(f"✅ {model_info['name']} loaded successfully!")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load {model_info['name']}: {str(e)}")
            raise
    
    @staticmethod
    def _create_vmamba_tmtb(checkpoint_path: str, device: str, **kwargs) -> nn.Module:
        """Create VMamba-TMTB model"""
        try:
            from ml.src.models.tmtb.vmamba_official import load_vmamba_model
            model = load_vmamba_model(checkpoint_path, device=device)
        except Exception as e:
            logger.warning(f"⚠️ Official VMamba failed: {e}")
            logger.info("🔄 Using custom TMTB implementation...")
            from ml.src.models.tmtb.vmamba_tmtb import load_vmamba_tmtb
            model = load_vmamba_tmtb(checkpoint_path, device=device)
        
        return model
    
    @staticmethod
    def _create_csrnet(checkpoint_path: str, device: str, **kwargs) -> nn.Module:
        """Create CSRNet model"""
        from models.csrnet import CSRNet
        
        model = CSRNet()
        
        if Path(checkpoint_path).exists():
            logger.info(f"📥 Loading CSRNet checkpoint from {checkpoint_path}")
            checkpoint = torch.load(checkpoint_path, map_location=device)
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if 'state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['state_dict'])
                elif 'model' in checkpoint:
                    model.load_state_dict(checkpoint['model'])
                else:
                    model.load_state_dict(checkpoint)
            else:
                model.load_state_dict(checkpoint)
            
            logger.info("✅ CSRNet checkpoint loaded successfully")
        else:
            logger.warning(f"⚠️ Checkpoint not found: {checkpoint_path}")
            logger.warning("🔧 Using randomly initialized CSRNet")
        
        model = model.to(device)
        model.eval()
        
        return model
    
    @staticmethod
    def _create_yolov8(checkpoint_path: str, device: str, **kwargs) -> Any:
        """Create YOLOv8 model"""
        try:
            from ultralytics import YOLO
        except ImportError:
            raise ImportError(
                "ultralytics not installed. Install with: pip install ultralytics"
            )
        
        if Path(checkpoint_path).exists():
            logger.info(f"📥 Loading YOLOv8 from {checkpoint_path}")
            model = YOLO(checkpoint_path)
        else:
            logger.warning(f"⚠️ Checkpoint not found: {checkpoint_path}")
            logger.info("📥 Downloading YOLOv8n pretrained model...")
            model = YOLO('yolov8n.pt')
        
        model.to(device)
        logger.info("✅ YOLOv8 loaded successfully")
        
        return model
    
    @staticmethod
    def _create_mcnn(checkpoint_path: str, device: str, **kwargs) -> nn.Module:
        """Create MCNN model"""
        from ml.src.models.mcnn.mcnn import MCNN
        
        model = MCNN()
        
        if Path(checkpoint_path).exists():
            logger.info(f"📥 Loading MCNN checkpoint from {checkpoint_path}")
            checkpoint = torch.load(checkpoint_path, map_location=device)
            
            if isinstance(checkpoint, dict):
                if 'state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['state_dict'])
                else:
                    model.load_state_dict(checkpoint)
            else:
                model.load_state_dict(checkpoint)
            
            logger.info("✅ MCNN checkpoint loaded successfully")
        else:
            logger.warning(f"⚠️ Checkpoint not found: {checkpoint_path}")
            logger.warning("🔧 Using randomly initialized MCNN")
        
        model = model.to(device)
        model.eval()
        
        return model
    
    @staticmethod
    def get_model_info(model_type: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model_type not in ModelFactory.SUPPORTED_MODELS:
            raise ValueError(f"Unknown model type: {model_type}")
        return ModelFactory.SUPPORTED_MODELS[model_type]
    
    @staticmethod
    def list_available_models() -> Dict[str, Dict[str, Any]]:
        """List all available models with their information"""
        return ModelFactory.SUPPORTED_MODELS
