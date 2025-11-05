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
    Supports: CSRNet, TMTB (VMamba), YOLO
    """
    
    def __init__(self):
        self.models = {}
        self.model_apis = {}
        self._load_model_apis()
    
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
            model_type: Model to use ('csrnet', 'tmtb', 'yolo')
            source: Source type for preprocessing
            return_density_map: Return density map (CSRNet/TMTB only)
            return_boxes: Return bounding boxes (YOLO only)
        
        Returns:
            Prediction results dictionary
        """
        model_type = model_type.lower()
        
        if model_type not in self.model_apis:
            raise ValueError(f"Unknown model type: {model_type}")
        
        api = self.model_apis[model_type]
        if api is None:
            raise RuntimeError(f"Model {model_type} is not available")
        
        logger.info(f"🔀 Routing to {model_type.upper()} model")
        
        # Route to appropriate model
        if model_type == 'csrnet':
            result = api.predict(
                image,
                source=source,
                return_density_map=return_density_map
            )
            result['model_name'] = 'CSRNet'
            
        elif model_type == 'tmtb':
            result = api.predict(
                image,
                source=source,
                return_density_map=return_density_map
            )
            result['model_name'] = 'TMTB'
            
        elif model_type == 'yolo':
            result = api.predict(
                image,
                source=source,
                return_boxes=return_boxes
            )
            result['model_name'] = 'YOLO'
        
        else:
            raise ValueError(f"Unsupported model: {model_type}")
        
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
            model_type: Model type
            result: Prediction result
            original_image: Original image
        
        Returns:
            Heatmap image (numpy array in BGR format)
        """
        model_type = model_type.lower()
        api = self.model_apis[model_type]
        
        if api is None:
            return None
        
        if model_type in ['csrnet', 'tmtb']:
            # Density map based heatmap
            if 'density_map' in result:
                return api.generate_heatmap(result['density_map'], original_image)
        
        elif model_type == 'yolo':
            # Box-based heatmap
            if 'boxes' in result and len(result['boxes']) > 0:
                return api.generate_heatmap(result['boxes'], original_image)
        
        return None
    
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
