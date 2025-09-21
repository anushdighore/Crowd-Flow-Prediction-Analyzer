import numpy as np
import torch
import torch.nn.functional as F
import cv2
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def get_count_from_density(density_map: np.ndarray, 
                          threshold: float = 0.01,
                          apply_gaussian: bool = True,
                          sigma: float = 1.0) -> float:
    """
    Convert density map to crowd count

    Args:
        density_map: 2D numpy array representing density map
        threshold: Minimum density value to consider (noise reduction)
        apply_gaussian: Whether to apply Gaussian smoothing
        sigma: Standard deviation for Gaussian kernel

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

        # Apply Gaussian smoothing to reduce noise
        if apply_gaussian and sigma > 0:
            density_map = cv2.GaussianBlur(density_map, (5, 5), sigma)

        # Apply threshold to remove noise
        density_map = np.maximum(density_map, 0)  # Ensure non-negative
        density_map[density_map < threshold] = 0

        # Sum all density values to get total count
        total_count = np.sum(density_map)

        logger.debug(f"Total count after processing: {total_count:.2f}")

        return float(total_count)

    except Exception as e:
        logger.error(f"Density to count conversion failed: {e}")
        # Return a reasonable fallback
        return 0.0

def get_count_with_classification(density_map: np.ndarray, 
                                cls_logits: Optional[np.ndarray] = None,
                                bins: list = None) -> Tuple[float, Optional[int]]:
    """
    Get count using both density map and classification head (if available)

    Args:
        density_map: 2D density map from regression head
        cls_logits: Classification logits for coarse bins (optional)
        bins: Bin boundaries for classification (optional)

    Returns:
        Tuple of (density_count, classification_bin)
    """
    # Get count from density map
    density_count = get_count_from_density(density_map)

    # Process classification if available
    classification_bin = None
    if cls_logits is not None:
        # Convert to probabilities
        probs = torch.softmax(torch.from_numpy(cls_logits), dim=-1)
        classification_bin = torch.argmax(probs).item()

        logger.debug(f"Classification bin: {classification_bin}, confidence: {probs[classification_bin]:.3f}")

    return density_count, classification_bin

def postprocess_density_map(density_map: torch.Tensor,
                           original_size: Tuple[int, int],
                           apply_sigmoid: bool = False) -> np.ndarray:
    """
    Postprocess model output density map

    Args:
        density_map: Model output tensor (B, 1, H, W) or (1, H, W) or (H, W)
        original_size: (height, width) of original image
        apply_sigmoid: Whether to apply sigmoid activation

    Returns:
        Processed density map as numpy array
    """
    try:
        # Handle different input shapes
        if len(density_map.shape) == 4:  # (B, 1, H, W)
            density_map = density_map.squeeze(0).squeeze(0)  # (H, W)
        elif len(density_map.shape) == 3:  # (1, H, W)
            density_map = density_map.squeeze(0)  # (H, W)
        elif len(density_map.shape) == 2:  # (H, W)
            pass  # Already correct shape
        else:
            raise ValueError(f"Unexpected density map shape: {density_map.shape}")

        # Apply sigmoid if requested (for some model variants)
        if apply_sigmoid:
            density_map = torch.sigmoid(density_map)

        # Ensure non-negative values
        density_map = torch.clamp(density_map, min=0)

        # Convert to numpy
        if isinstance(density_map, torch.Tensor):
            density_np = density_map.detach().cpu().numpy()
        else:
            density_np = density_map

        # Resize to match original aspect ratio if needed
        if original_size and original_size != density_np.shape:
            # Calculate target size maintaining aspect ratio
            h_orig, w_orig = original_size
            h_density, w_density = density_np.shape

            # Resize using OpenCV
            density_resized = cv2.resize(
                density_np, 
                (w_orig // 4, h_orig // 4),  # Quarter resolution is typical
                interpolation=cv2.INTER_LINEAR
            )

            logger.debug(f"Resized density map from {density_np.shape} to {density_resized.shape}")
            return density_resized

        return density_np

    except Exception as e:
        logger.error(f"Density map postprocessing failed: {e}")
        # Return zeros as fallback
        return np.zeros((original_size[0]//4, original_size[1]//4), dtype=np.float32)

def visualize_density_map(density_map: np.ndarray, 
                         colormap: int = cv2.COLORMAP_JET,
                         normalize: bool = True) -> np.ndarray:
    """
    Create visualization of density map for debugging

    Args:
        density_map: 2D density map
        colormap: OpenCV colormap for visualization
        normalize: Whether to normalize values to [0, 255]

    Returns:
        Colored density map visualization
    """
    try:
        # Normalize to 0-255 range
        if normalize:
            if density_map.max() > density_map.min():
                normalized = ((density_map - density_map.min()) / 
                            (density_map.max() - density_map.min()) * 255)
            else:
                normalized = np.zeros_like(density_map)
        else:
            normalized = np.clip(density_map * 255, 0, 255)

        # Convert to uint8
        heatmap = normalized.astype(np.uint8)

        # Apply colormap
        colored_heatmap = cv2.applyColorMap(heatmap, colormap)

        return colored_heatmap

    except Exception as e:
        logger.error(f"Density map visualization failed: {e}")
        return np.zeros((density_map.shape[0], density_map.shape[1], 3), dtype=np.uint8)

def adaptive_count_correction(raw_count: float, 
                            density_map: np.ndarray,
                            correction_factor: float = 1.0) -> float:
    """
    Apply adaptive correction to crowd count based on density distribution

    Args:
        raw_count: Raw count from density map summation
        density_map: Original density map for analysis
        correction_factor: Manual correction factor

    Returns:
        Corrected crowd count
    """
    try:
        # Basic correction based on density distribution
        non_zero_pixels = np.sum(density_map > 0.01)
        total_pixels = density_map.size

        # Density coverage ratio
        coverage_ratio = non_zero_pixels / total_pixels

        # Apply corrections based on coverage
        if coverage_ratio > 0.8:  # Very dense crowd
            corrected_count = raw_count * 0.95  # Slight reduction to avoid over-counting
        elif coverage_ratio > 0.5:  # Medium density
            corrected_count = raw_count * correction_factor
        elif coverage_ratio > 0.1:  # Sparse crowd
            corrected_count = raw_count * 1.05  # Slight increase
        else:  # Very sparse or empty
            corrected_count = raw_count

        logger.debug(f"Count correction: {raw_count:.2f} → {corrected_count:.2f} (coverage: {coverage_ratio:.3f})")

        return max(0.0, corrected_count)  # Ensure non-negative

    except Exception as e:
        logger.error(f"Count correction failed: {e}")
        return raw_count

def get_density_statistics(density_map: np.ndarray) -> dict:
    """
    Get statistical information about the density map

    Args:
        density_map: 2D density map

    Returns:
        Dictionary with density statistics
    """
    try:
        stats = {
            'total_count': float(np.sum(density_map)),
            'max_density': float(np.max(density_map)),
            'mean_density': float(np.mean(density_map)),
            'std_density': float(np.std(density_map)),
            'non_zero_pixels': int(np.sum(density_map > 0.01)),
            'coverage_ratio': float(np.sum(density_map > 0.01) / density_map.size),
            'shape': density_map.shape
        }

        return stats

    except Exception as e:
        logger.error(f"Density statistics calculation failed: {e}")
        return {
            'total_count': 0.0,
            'max_density': 0.0,
            'mean_density': 0.0,
            'std_density': 0.0,
            'non_zero_pixels': 0,
            'coverage_ratio': 0.0,
            'shape': (0, 0)
        }

def multi_scale_count(density_map: np.ndarray, scales: list = [1.0, 0.5, 0.25]) -> dict:
    """
    Perform multi-scale counting for improved accuracy

    Args:
        density_map: Original density map
        scales: List of scales to apply

    Returns:
        Dictionary with counts at different scales
    """
    try:
        results = {}

        for scale in scales:
            if scale == 1.0:
                scaled_map = density_map
            else:
                # Resize density map
                h, w = density_map.shape
                new_h, new_w = int(h * scale), int(w * scale)
                scaled_map = cv2.resize(density_map, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                # Scale the values to maintain count consistency
                scaled_map = scaled_map / (scale * scale)

            count = get_count_from_density(scaled_map)
            results[f'scale_{scale}'] = count

        # Compute weighted average
        weights = [1.0, 0.5, 0.25]  # Give more weight to full scale
        weighted_count = sum(results[f'scale_{scale}'] * weight 
                           for scale, weight in zip(scales, weights)) / sum(weights)

        results['weighted_average'] = weighted_count

        return results

    except Exception as e:
        logger.error(f"Multi-scale counting failed: {e}")
        return {'weighted_average': get_count_from_density(density_map)}

# Export main functions
__all__ = [
    'get_count_from_density', 
    'get_count_with_classification',
    'postprocess_density_map',
    'visualize_density_map',
    'adaptive_count_correction',
    'get_density_statistics',
    'multi_scale_count'
]
