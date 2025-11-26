"""
YOLOv8 Wrapper for Crowd Counting
Uses YOLOv8 object detection to count people in images/video
"""

import torch
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class YOLOv8Counter:
    """
    Wrapper class for YOLOv8-based crowd counting
    Detects and counts people using YOLOv8
    """
    
    def __init__(
        self,
        model_path: str = 'yolov8n.pt',
        device: str = 'cuda',
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45
    ):
        """
        Initialize YOLOv8 counter
        
        Args:
            model_path: Path to YOLOv8 model
            device: Device to run model on
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
        """
        try:
            from ultralytics import YOLO
        except ImportError:
            raise ImportError(
                "ultralytics not installed. Install with: pip install ultralytics"
            )
        
        self.device = device
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        
        # Load model - check multiple locations
        logger.info(f"🔧 Loading YOLOv8 model from {model_path}...")
        
        # Try multiple paths: direct, backend folder, ml folder
        backend_path = Path(__file__).parent.parent.parent.parent.parent / "backend" / model_path
        possible_paths = [
            Path(model_path),  # Direct path
            backend_path,      # backend/yolov8*.pt
            Path(__file__).parent / model_path,  # Same folder as this file
        ]
        
        model_found = False
        for check_path in possible_paths:
            if check_path.exists():
                logger.info(f"✅ Found model at {check_path}")
                self.model = YOLO(str(check_path))
                model_found = True
                break
        
        if not model_found:
            logger.warning(f"⚠️ Model not found at {model_path}, tried: {[str(p) for p in possible_paths]}")
            logger.info("📥 Downloading YOLOv8n pretrained model...")
            self.model = YOLO('yolov8n.pt')
        
        self.model.to(device)
        logger.info(f"✅ YOLOv8 loaded on {device}")
        
        # COCO person class ID
        self.PERSON_CLASS_ID = 0
    
    def predict(
        self,
        image: np.ndarray,
        return_boxes: bool = False,
        visualize: bool = False
    ) -> Dict:
        """
        Detect and count people in image
        
        Args:
            image: Input image (H, W, 3) in RGB format
            return_boxes: Whether to return bounding boxes
            visualize: Whether to return annotated image
            
        Returns:
            Dictionary with count, boxes (optional), and annotated image (optional)
        """
        # Run inference
        results = self.model.predict(
            image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=[self.PERSON_CLASS_ID],  # Only detect persons
            device=self.device,
            verbose=False
        )
        
        # Extract results
        result = results[0]
        boxes = result.boxes
        
        # Count people
        count = len(boxes)
        
        output = {
            'count': count,
            'confidence': self.conf_threshold
        }
        
        # Add bounding boxes if requested
        if return_boxes and count > 0:
            boxes_xyxy = boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
            confidences = boxes.conf.cpu().numpy()
            
            output['boxes'] = [
                {
                    'bbox': box.tolist(),
                    'confidence': float(conf)
                }
                for box, conf in zip(boxes_xyxy, confidences)
            ]
        
        # Add annotated image if requested
        if visualize:
            annotated_image = result.plot()  # Returns BGR image
            output['annotated_image'] = annotated_image
        
        return output
    
    def predict_batch(
        self,
        images: List[np.ndarray],
        return_boxes: bool = False
    ) -> List[Dict]:
        """
        Batch prediction for multiple images
        
        Args:
            images: List of input images
            return_boxes: Whether to return bounding boxes
            
        Returns:
            List of prediction dictionaries
        """
        results = self.model.predict(
            images,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=[self.PERSON_CLASS_ID],
            device=self.device,
            verbose=False
        )
        
        outputs = []
        for result in results:
            boxes = result.boxes
            count = len(boxes)
            
            output = {
                'count': count,
                'confidence': self.conf_threshold
            }
            
            if return_boxes and count > 0:
                boxes_xyxy = boxes.xyxy.cpu().numpy()
                confidences = boxes.conf.cpu().numpy()
                
                output['boxes'] = [
                    {
                        'bbox': box.tolist(),
                        'confidence': float(conf)
                    }
                    for box, conf in zip(boxes_xyxy, confidences)
                ]
            
            outputs.append(output)
        
        return outputs
    
    def __call__(self, image: np.ndarray) -> int:
        """
        Simple call interface for counting
        
        Args:
            image: Input image
            
        Returns:
            Person count
        """
        result = self.predict(image, return_boxes=False)
        return result['count']


def load_yolov8_counter(
    checkpoint_path: str = 'yolov8n.pt',
    device: str = 'cuda',
    **kwargs
) -> YOLOv8Counter:
    """
    Load YOLOv8 counter with specified configuration
    
    Args:
        checkpoint_path: Path to YOLOv8 model
        device: Device to run on
        **kwargs: Additional arguments for YOLOv8Counter
        
    Returns:
        Initialized YOLOv8Counter
    """
    logger.info("🔧 Initializing YOLOv8 Counter...")
    counter = YOLOv8Counter(
        model_path=checkpoint_path,
        device=device,
        **kwargs
    )
    logger.info("✅ YOLOv8 Counter ready!")
    return counter


if __name__ == "__main__":
    # Test the counter
    logging.basicConfig(level=logging.INFO)
    
    try:
        counter = YOLOv8Counter(device='cuda' if torch.cuda.is_available() else 'cpu')
        
        # Test with random image
        test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        result = counter.predict(test_image, return_boxes=True)
        
        print(f"✅ YOLOv8 Counter test successful!")
        print(f"Detected count: {result['count']}")
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install ultralytics with: pip install ultralytics")
