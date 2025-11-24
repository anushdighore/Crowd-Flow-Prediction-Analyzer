"""YOLO API - Unified interface for crowd counting"""
import time
from pathlib import Path
from PIL import Image
from typing import Dict, Union
import logging
import numpy as np
import cv2

logger = logging.getLogger(__name__)

_model_cache = {}


def get_model(checkpoint_path: str = None):
    """Get cached YOLO model or load new one"""
    global _model_cache
    if checkpoint_path is None:
        checkpoint_path = "yolov8n.pt"  # Default to YOLOv8 nano
    
    if checkpoint_path in _model_cache:
        return _model_cache[checkpoint_path]
    
    from .yolov8_counter import YOLOv8Counter
    import torch
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLOv8Counter(model_path=checkpoint_path, device=device)
    _model_cache[checkpoint_path] = model
    return model


def predict(image: Union[str, Path, Image.Image], checkpoint_path: str = None, source: str = "image", return_boxes: bool = False, visualize: bool = False) -> Dict:
    """Run YOLO prediction for crowd counting
    
    Args:
        image: Input image (path or PIL Image)
        checkpoint_path: Path to model checkpoint
        source: Input source type (for compatibility)
        return_boxes: Whether to return bounding boxes
        visualize: Whether to return annotated image
    """
    start_time = time.time()
    
    # Load and convert image
    if isinstance(image, (str, Path)):
        img = Image.open(image).convert('RGB')
    else:
        img = image.convert('RGB')
    
    original_size = img.size
    
    # Convert to numpy array (RGB)
    img_np = np.array(img)
    
    # Get model
    model = get_model(checkpoint_path)
    
    # Run inference - only pass visualize if True to avoid compatibility issues
    if visualize:
        result = model.predict(img_np, return_boxes=return_boxes, visualize=True)
    else:
        result = model.predict(img_np, return_boxes=return_boxes)
    
    inference_time = (time.time() - start_time) * 1000
    
    # Prepare response
    response = {
        "count": float(result['count']),
        "rounded_count": int(result['count']),
        "inference_time_ms": float(inference_time),
        "device": str(model.device),
        "original_size": original_size,
        "source": source,
        "model_type": "yolo"
    }
    
    # Add boxes if requested and transform to expected format
    if return_boxes and 'boxes' in result and len(result['boxes']) > 0:
        # Transform boxes from {bbox: [...], confidence: ...} to {x1, y1, x2, y2, confidence}
        transformed_boxes = []
        confidences = []
        
        logger.info(f"📦 Transforming {len(result['boxes'])} boxes from YOLOv8Counter format")
        
        for box_info in result['boxes']:
            bbox = box_info['bbox']
            conf = box_info['confidence']
            confidences.append(conf)
            
            transformed_boxes.append({
                'x1': int(bbox[0]),
                'y1': int(bbox[1]),
                'x2': int(bbox[2]),
                'y2': int(bbox[3]),
                'confidence': float(conf)
            })
        
        response["boxes"] = transformed_boxes
        logger.info(f"✅ Transformed boxes: {len(transformed_boxes)} boxes in x1,y1,x2,y2 format")
        
        # Calculate confidence statistics
        if confidences:
            response["average_confidence"] = float(np.mean(confidences))
            response["min_confidence"] = float(np.min(confidences))
            response["max_confidence"] = float(np.max(confidences))
    
    # Add annotated image if available (for visualization)
    if 'annotated_image' in result:
        response["annotated_image"] = result['annotated_image']
    
    return response


def generate_heatmap(boxes: list, original_image: Image.Image) -> np.ndarray:
    """Generate heatmap from YOLO detection boxes
    
    Args:
        boxes: List of box dictionaries with bbox and confidence OR x1,y1,x2,y2 format
        original_image: Original PIL image
        
    Returns:
        BGR image with heatmap overlay
    """
    # Safety check for empty boxes
    if not boxes or len(boxes) == 0:
        logger.warning("⚠️ No boxes provided to generate_heatmap, returning original image")
        # Return original image as BGR
        import cv2
        original_bgr = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)
        return original_bgr
    
    logger.info(f"🎨 Generating heatmap for {len(boxes)} boxes")
    logger.debug(f"📋 First box format: {boxes[0].keys() if boxes else 'N/A'}")
    
    # Create density map from boxes
    width, height = original_image.size
    density_map = np.zeros((height, width), dtype=np.float32)
    
    # Add Gaussian blobs for each detection
    for box_info in boxes:
        try:
            # Handle both formats: {bbox: [...]} and {x1, y1, x2, y2}
            if 'bbox' in box_info:
                bbox = box_info['bbox']  # [x1, y1, x2, y2]
                x1, y1, x2, y2 = map(int, bbox)
            else:
                # Already in x1, y1, x2, y2 format
                x1 = int(box_info['x1'])
                y1 = int(box_info['y1'])
                x2 = int(box_info['x2'])
                y2 = int(box_info['y2'])
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"❌ Error parsing box {box_info}: {e}")
            continue
        
        # Center of box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        
        # Size-based sigma
        w = x2 - x1
        h = y2 - y1
        sigma = max(w, h) // 4
        
        # Create Gaussian kernel
        size = sigma * 3
        y, x = np.ogrid[-size:size+1, -size:size+1]
        gaussian = np.exp(-(x*x + y*y) / (2.*sigma*sigma))
        
        # Add to density map
        y1_g = max(0, cy - size)
        y2_g = min(height, cy + size + 1)
        x1_g = max(0, cx - size)
        x2_g = min(width, cx + size + 1)
        
        g_y1 = size - (cy - y1_g)
        g_y2 = g_y1 + (y2_g - y1_g)
        g_x1 = size - (cx - x1_g)
        g_x2 = g_x1 + (x2_g - x1_g)
        
        density_map[y1_g:y2_g, x1_g:x2_g] += gaussian[g_y1:g_y2, g_x1:g_x2]
    
    # Normalize to 0-255
    if density_map.max() > 0:
        density_normalized = (density_map / density_map.max() * 255).astype(np.uint8)
    else:
        density_normalized = density_map.astype(np.uint8)
    
    # Apply colormap
    heatmap = cv2.applyColorMap(density_normalized, cv2.COLORMAP_JET)
    
    # Convert original image to BGR
    original_bgr = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)
    
    # Blend
    overlay = cv2.addWeighted(original_bgr, 0.4, heatmap, 0.6, 0)
    
    return overlay
