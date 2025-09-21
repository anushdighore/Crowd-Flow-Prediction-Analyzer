import cv2
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
import logging

logger = logging.getLogger(__name__)

def preprocess_frame(img: np.ndarray, target_size: int = 512) -> torch.Tensor:
    """
    Preprocess image frame for VMamba-TMTB model inference

    Args:
        img: Input image as numpy array (H, W, 3) in BGR format from OpenCV
        target_size: Target size for model input (default: 512)

    Returns:
        Preprocessed tensor (3, target_size, target_size) ready for model input
    """
    try:
        # Convert BGR to RGB
        if len(img.shape) == 3 and img.shape[2] == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img

        # Get original dimensions
        h, w = img_rgb.shape[:2]
        logger.debug(f"Original image size: {w}x{h}")

        # Resize while maintaining aspect ratio
        # Find the larger dimension and scale accordingly
        scale = target_size / max(h, w)
        new_h = int(h * scale)
        new_w = int(w * scale)

        # Resize image
        img_resized = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Create square canvas and center the image
        canvas = np.zeros((target_size, target_size, 3), dtype=np.uint8)

        # Calculate padding to center the image
        y_offset = (target_size - new_h) // 2
        x_offset = (target_size - new_w) // 2

        # Place resized image on canvas
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized

        # CRITICAL FIX: Convert to float32 (was causing the error!)
        img_normalized = canvas.astype(np.float32) / 255.0

        # Apply ImageNet normalization (standard for vision models)
        # CRITICAL FIX: Ensure mean/std arrays are float32
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

        img_normalized = (img_normalized - mean) / std

        # Convert to torch tensor and change from HWC to CHW format
        img_tensor = torch.from_numpy(img_normalized).permute(2, 0, 1)

        # CRITICAL FIX: Ensure tensor is float32
        img_tensor = img_tensor.float()

        logger.debug(f"Preprocessed tensor shape: {img_tensor.shape}, dtype: {img_tensor.dtype}")

        return img_tensor

    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise ValueError(f"Image preprocessing error: {e}")

def preprocess_batch(images: list, target_size: int = 512) -> torch.Tensor:
    """
    Preprocess a batch of images for inference

    Args:
        images: List of numpy arrays (images)
        target_size: Target size for model input

    Returns:
        Batch tensor (B, 3, target_size, target_size)
    """
    batch_tensors = []

    for img in images:
        processed = preprocess_frame(img, target_size)
        batch_tensors.append(processed)

    # Stack into batch
    batch_tensor = torch.stack(batch_tensors, dim=0)

    # CRITICAL FIX: Ensure batch is float32
    batch_tensor = batch_tensor.float()

    logger.debug(f"Batch tensor shape: {batch_tensor.shape}, dtype: {batch_tensor.dtype}")

    return batch_tensor

def get_preprocessing_transform(target_size: int = 512):
    """
    Get torchvision transform for preprocessing (alternative approach)

    Args:
        target_size: Target image size

    Returns:
        Composed transform
    """
    return transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((target_size, target_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

# Export main function
__all__ = ['preprocess_frame', 'preprocess_batch', 'get_preprocessing_transform']
