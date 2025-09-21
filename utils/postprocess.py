import numpy as np
import torch
import torch.nn.functional as F
import cv2
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def detect_image_type(density_map: np.ndarray) -> str:
    """
    Detect if image is likely a crowd vs portrait/single person

    Args:
        density_map: 2D density map from model

    Returns:
        'crowd', 'portrait', or 'few_people'
    """
    try:
        # Calculate density statistics
        total_activation = np.sum(density_map)
        max_density = np.max(density_map)
        mean_density = np.mean(density_map[density_map > 0.01])
        coverage_ratio = np.sum(density_map > 0.01) / density_map.size

        logger.debug(f"Image analysis: total={total_activation:.2f}, max={max_density:.2f}, coverage={coverage_ratio:.3f}")

        # Classification logic based on density patterns
        if coverage_ratio < 0.05 and total_activation < 50:
            return 'portrait'  # Very localized activation
        elif coverage_ratio < 0.15 and total_activation < 100:
            return 'few_people'  # Small group
        else:
            return 'crowd'  # Actual crowd

    except:
        return 'crowd'  # Default to crowd if analysis fails

def smart_count_calibration(raw_count: float, 
                          density_map: np.ndarray,
                          image_type: str = None) -> float:
    """
    Apply intelligent calibration based on image content

    Args:
        raw_count: Raw count from density summation
        density_map: Original density map
        image_type: Detected image type

    Returns:
        Calibrated crowd count
    """
    try:
        if image_type is None:
            image_type = detect_image_type(density_map)

        logger.info(f"🔍 Detected image type: {image_type}")

        # Apply different calibration factors based on image type
        if image_type == 'portrait':
            # For single person images, apply heavy correction
            calibrated = min(raw_count * 0.01, 3.0)  # Cap at 3 people max
            logger.info(f"📸 Portrait mode: {raw_count:.1f} → {calibrated:.1f}")

        elif image_type == 'few_people':
            # For small groups, moderate correction
            calibrated = raw_count * 0.05
            calibrated = min(calibrated, 20.0)  # Cap at 20 people
            logger.info(f"👥 Few people mode: {raw_count:.1f} → {calibrated:.1f}")

        else:  # crowd
            # For actual crowds, lighter correction
            calibrated = raw_count * 0.3
            logger.info(f"🏟️ Crowd mode: {raw_count:.1f} → {calibrated:.1f}")

        return max(0.0, calibrated)

    except Exception as e:
        logger.error(f"Calibration failed: {e}")
        return max(0.0, raw_count * 0.1)  # Conservative fallback

def get_count_from_density(density_map: np.ndarray, 
                          threshold: float = 0.05,  # Increased threshold
                          apply_gaussian: bool = True,
                          sigma: float = 2.0,  # Increased smoothing
                          use_smart_calibration: bool = True) -> float:
    """
    Convert density map to crowd count with smart calibration

    Args:
        density_map: 2D numpy array representing density map
        threshold: Minimum density value to consider (increased)
        apply_gaussian: Whether to apply Gaussian smoothing
        sigma: Standard deviation for Gaussian kernel (increased)
        use_smart_calibration: Whether to use intelligent calibration

    Returns:
        Estimated crowd count as float
    """
    try:
        # Ensure 2D array
        if len(density_map.shape) > 2:
            density_map = np.squeeze(density_map)

        if len(density_map.shape) != 2:
            raise ValueError(f"Expected 2D density map, got shape: {density_map.shape}")

        logger.debug(f"Density map shape: {density_map.shape}, range: [{density_map.min():.4f}, {density_map.max():.4f}]")

        # Apply stronger Gaussian smoothing to reduce noise
        if apply_gaussian and sigma > 0:
            kernel_size = int(6 * sigma + 1)  # Larger kernel
            if kernel_size % 2 == 0:
                kernel_size += 1
            density_map = cv2.GaussianBlur(density_map, (kernel_size, kernel_size), sigma)

        # Apply higher threshold to remove noise
        density_map = np.maximum(density_map, 0)  # Ensure non-negative
        density_map[density_map < threshold] = 0

        # Sum all density values to get raw count
        raw_count = np.sum(density_map)

        logger.debug(f"Raw count after thresholding: {raw_count:.2f}")

        # Apply smart calibration if enabled
        if use_smart_calibration:
            final_count = smart_count_calibration(raw_count, density_map)
        else:
            final_count = raw_count

        logger.info(f"Final count: {final_count:.1f}")

        return float(final_count)

    except Exception as e:
        logger.error(f"Density to count conversion failed: {e}")
        return 0.0

def get_count_with_classification(density_map: np.ndarray, 
                                cls_logits: Optional[np.ndarray] = None,
                                bins: list = None) -> Tuple[float, Optional[int]]:
    """
    Get count using both density map and classification head (if available)
    """
    # Get count from density map with smart calibration
    density_count = get_count_from_density(density_map, use_smart_calibration=True)

    # Process classification if available
    classification_bin = None
    if cls_logits is not None:
        probs = torch.softmax(torch.from_numpy(cls_logits), dim=-1)
        classification_bin = torch.argmax(probs).item()
        logger.debug(f"Classification bin: {classification_bin}, confidence: {probs[classification_bin]:.3f}")

    return density_count, classification_bin

def postprocess_density_map(density_map: torch.Tensor,
                           original_size: Tuple[int, int],
                           apply_sigmoid: bool = False) -> np.ndarray:
    """
    Postprocess model output density map
    """
    try:
        # Handle different input shapes
        if len(density_map.shape) == 4:  # (B, 1, H, W)
            density_map = density_map.squeeze(0).squeeze(0)  # (H, W)
        elif len(density_map.shape) == 3:  # (1, H, W)
            density_map = density_map.squeeze(0)  # (H, W)

        # Apply sigmoid if requested
        if apply_sigmoid:
            density_map = torch.sigmoid(density_map)

        # Ensure non-negative values
        density_map = torch.clamp(density_map, min=0)

        # Convert to numpy
        if isinstance(density_map, torch.Tensor):
            density_np = density_map.detach().cpu().numpy()
        else:
            density_np = density_map

        # Resize if needed
        if original_size and original_size != density_np.shape:
            h_orig, w_orig = original_size
            density_resized = cv2.resize(
                density_np, 
                (w_orig // 4, h_orig // 4),
                interpolation=cv2.INTER_LINEAR
            )
            return density_resized

        return density_np

    except Exception as e:
        logger.error(f"Density map postprocessing failed: {e}")
        return np.zeros((original_size[0]//4, original_size[1]//4), dtype=np.float32)

def visualize_density_map(density_map: np.ndarray, 
                         colormap: int = cv2.COLORMAP_JET,
                         normalize: bool = True) -> np.ndarray:
    """Create visualization of density map for debugging"""
    try:
        if normalize:
            if density_map.max() > density_map.min():
                normalized = ((density_map - density_map.min()) / 
                            (density_map.max() - density_map.min()) * 255)
            else:
                normalized = np.zeros_like(density_map)
        else:
            normalized = np.clip(density_map * 255, 0, 255)

        heatmap = normalized.astype(np.uint8)
        colored_heatmap = cv2.applyColorMap(heatmap, colormap)
        return colored_heatmap

    except Exception as e:
        logger.error(f"Density map visualization failed: {e}")
        return np.zeros((density_map.shape[0], density_map.shape[1], 3), dtype=np.uint8)

# Export main functions
__all__ = [
    'get_count_from_density', 
    'get_count_with_classification',
    'postprocess_density_map',
    'visualize_density_map',
    'smart_count_calibration',
    'detect_image_type'
]
