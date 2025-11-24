# backend/app/services/ml_processor.py
import cv2
import numpy as np
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add ml/src to path
ML_SRC = Path(__file__).parent.parent.parent.parent / "ml" / "src"
sys.path.insert(0, str(ML_SRC))

from models.unified_counter import UnifiedCounter

logger = logging.getLogger(__name__)


class MLProcessor:
    """ML Processing service with V3 tracking support"""
    
    def __init__(
        self,
        model_type: str = 'yolo',
        model_path: Optional[str] = None,
        enable_tracking: bool = False,
        device: str = 'cuda'
    ):
        """
        Initialize ML processor
        
        Args:
            model_type: 'yolo', 'csrnet', or 'mcnn'
            model_path: Path to model weights
            enable_tracking: Enable Kalman filter tracking (YOLO only)
            device: 'cuda' or 'cpu'
        """
        self.model_type = model_type
        self.enable_tracking = enable_tracking
        
        try:
            self.counter = UnifiedCounter(
                model_type=model_type,
                model_path=model_path,
                device=device,
                enable_tracking=enable_tracking,
                conf_threshold=0.25,
                iou_threshold=0.45
            )
            logger.info(f"Initialized {model_type} model (tracking={enable_tracking})")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            self.counter = None
    
    def process_frame(self, frame: np.ndarray, return_details: bool = True) -> Dict[str, Any]:
        """
        Process a single frame with ML model
        
        Args:
            frame: Input frame (BGR)
            return_details: Return detailed prediction info
            
        Returns:
            Dictionary with results including annotated frame
        """
        if self.counter is None:
            # Fallback: return original frame
            return {
                'count': 0,
                'annotated_frame': frame,
                'error': 'Model not initialized'
            }
        
        try:
            # Get prediction with visualization
            result = self.counter.predict(
                frame,
                return_details=return_details,
                return_visualization=True
            )
            
            # Add annotated frame to result
            if 'annotated_image' in result:
                result['annotated_frame'] = result['annotated_image']
            else:
                result['annotated_frame'] = frame
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return {
                'count': 0,
                'annotated_frame': frame,
                'error': str(e)
            }
    
    def reset_tracking(self):
        """Reset tracker state"""
        if self.counter:
            self.counter.reset_tracker()


# Singleton instance - default YOLO with tracking
ml_processor = MLProcessor(
    model_type='yolo',
    enable_tracking=True,
    device='cuda'
)