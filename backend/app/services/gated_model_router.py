"""
Gated Modular Architecture for Model Selection
Routes requests to appropriate models based on user selection
"""
import logging
from typing import Dict, Any
from PIL import Image
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Add ml/src to path
ml_path = Path(__file__).parent.parent.parent.parent / "ml" / "src"
if str(ml_path) not in sys.path:
    sys.path.insert(0, str(ml_path))


class GatedModelRouter:
    """
    Gated architecture that routes requests to the appropriate model
    Supports: CSRNet, TMTB (VMamba), YOLO (with variants: nano, small, medium, large, xlarge)
    """
    
    # YOLO variant to checkpoint mapping
    YOLO_VARIANT_MAP = {
        "yolo": "yolov8n.pt",
        "yolo-nano": "yolov8n.pt",
        "yolo-small": "yolov8s.pt",
        "yolo-medium": "yolov8m.pt",
        "yolo-large": "yolov8l.pt",
        "yolo-xlarge": "yolov8x.pt",
    }
    
    def __init__(self):
        self.models = {}
        self.model_apis = {}
        self._load_model_apis()
    
    def _normalize_model_type(self, model_type: str) -> tuple:
        """
        Normalize model type and extract YOLO checkpoint if applicable.
        
        Args:
            model_type: Raw model type string (e.g., 'yolo-xlarge', 'csrnet')
            
        Returns:
            Tuple of (normalized_type, yolo_checkpoint or None)
        """
        model_type = model_type.lower()
        
        # Handle YOLO variants
        if model_type.startswith("yolo"):
            checkpoint = self.YOLO_VARIANT_MAP.get(model_type, "yolov8n.pt")
            return ("yolo", checkpoint)
        
        return (model_type, None)
    
    def _load_model_apis(self):
        """Load all available model APIs"""
        # Load CSRNet
        try:
            from models.csrnet import api as csrnet_api
            self.model_apis['csrnet'] = csrnet_api
            logger.info("✅ CSRNet API loaded")
        except ImportError as e:
            logger.warning(f"⚠️ CSRNet API not available: {e}")
            self.model_apis['csrnet'] = None
        
        # Load TMTB
        try:
            from models.tmtb import api as tmtb_api
            self.model_apis['tmtb'] = tmtb_api
            logger.info("✅ TMTB API loaded")
        except ImportError as e:
            logger.warning(f"⚠️ TMTB API not available: {e}")
            self.model_apis['tmtb'] = None
        
        # Load YOLO
        try:
            from models.yolo import api as yolo_api
            self.model_apis['yolo'] = yolo_api
            logger.info("✅ YOLO API loaded")
        except ImportError as e:
            logger.warning(f"⚠️ YOLO API not available: {e}")
            self.model_apis['yolo'] = None
    
    def predict(
        self,
        image: Image.Image,
        model_type: str,
        source: str = "surveillance",
        return_density_map: bool = False,
        return_boxes: bool = False
    ) -> Dict[str, Any]:
        """
        Route prediction to appropriate model
        
        Args:
            image: PIL Image
            model_type: Model to use ('csrnet', 'tmtb', 'yolo', 'yolo-nano', 'yolo-small', etc.)
            source: Source type for preprocessing
            return_density_map: Return density map (CSRNet/TMTB only)
            return_boxes: Return bounding boxes (YOLO only)
        
        Returns:
            Prediction results dictionary
        """
        original_model_type = model_type
        normalized_type, yolo_checkpoint = self._normalize_model_type(model_type)
        
        if normalized_type not in self.model_apis:
            raise ValueError(f"Unknown model type: {model_type}")
        
        api = self.model_apis[normalized_type]
        if api is None:
            raise RuntimeError(f"Model {normalized_type} is not available")
        
        logger.info(f"🔀 Routing to {normalized_type.upper()} model" + 
                   (f" (checkpoint: {yolo_checkpoint})" if yolo_checkpoint else ""))
        
        # Route to appropriate model
        if normalized_type == 'csrnet':
            result = api.predict(
                image,
                source=source,
                return_density_map=return_density_map
            )
            result['model_name'] = 'CSRNet'
            
        elif normalized_type == 'tmtb':
            result = api.predict(
                image,
                source=source,
                return_density_map=return_density_map
            )
            result['model_name'] = 'TMTB'
            
        elif normalized_type == 'yolo':
            result = api.predict(
                image,
                checkpoint_path=yolo_checkpoint,
                source=source,
                return_boxes=return_boxes
            )
            # Set model name based on variant
            variant_name = original_model_type.upper().replace("YOLO-", "YOLO-") if "-" in original_model_type else "YOLO-NANO"
            result['model_name'] = variant_name
        
        else:
            raise ValueError(f"Unsupported model: {normalized_type}")
        
        # Store original model type for reference
        result['original_model_type'] = original_model_type
        
        return result
    
    def generate_heatmap(
        self,
        model_type: str,
        result: Dict[str, Any],
        original_image: Image.Image
    ) -> Any:
        """
        Generate heatmap based on model type
        
        Args:
            model_type: Model type (supports variants like 'yolo-xlarge')
            result: Prediction result
            original_image: Original image
        
        Returns:
            Heatmap image (numpy array in BGR format)
        """
        normalized_type, _ = self._normalize_model_type(model_type)
        api = self.model_apis[normalized_type]
        
        if api is None:
            return None
        
        if normalized_type in ['csrnet', 'tmtb']:
            # Density map based heatmap
            if 'density_map' in result:
                return api.generate_heatmap(result['density_map'], original_image)
        
        elif normalized_type == 'yolo':
            # Box-based heatmap
            if 'boxes' in result and len(result['boxes']) > 0:
                return api.generate_heatmap(result['boxes'], original_image)
        
        return None
    
    def is_yolo_variant(self, model_type: str) -> bool:
        """Check if model type is a YOLO variant"""
        return model_type.lower().startswith("yolo")
    
    def get_yolo_checkpoint(self, model_type: str) -> str:
        """Get YOLO checkpoint path for a model type"""
        return self.YOLO_VARIANT_MAP.get(model_type.lower(), "yolov8n.pt")
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        return [name for name, api in self.model_apis.items() if api is not None]


# Global router instance
_router = None

def get_router() -> GatedModelRouter:
    """Get or create global router instance"""
    global _router
    if _router is None:
        _router = GatedModelRouter()
    return _router
