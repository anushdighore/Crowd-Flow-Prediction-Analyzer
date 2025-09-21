import numpy as np
import torch
import torch.nn.functional as F
import cv2
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def analyze_density_map(density_map: np.ndarray) -> dict:
    """
    Analyze density map characteristics to inform calibration

    Args:
        density_map: 2D density map from model

    Returns:
        Dictionary with analysis results
    """
    try:
        # Basic statistics
        total_sum = np.sum(density_map)
        max_value = np.max(density_map)
        mean_nonzero = np.mean(density_map[density_map > 0.001]) if np.any(density_map > 0.001) else 0

        # Coverage analysis
        low_threshold = 0.001
        med_threshold = 0.01
        high_threshold = 0.05

        low_coverage = np.sum(density_map > low_threshold) / density_map.size
        med_coverage = np.sum(density_map > med_threshold) / density_map.size
        high_coverage = np.sum(density_map > high_threshold) / density_map.size

        # Peak detection
        num_peaks = len(find_local_maxima(density_map, threshold=max_value * 0.3))

        return {
            'total_sum': total_sum,
            'max_value': max_value,
            'mean_nonzero': mean_nonzero,
            'low_coverage': low_coverage,
            'med_coverage': med_coverage,
            'high_coverage': high_coverage,
            'num_peaks': num_peaks
        }

    except Exception as e:
        logger.error(f"Density analysis failed: {e}")
        return {'total_sum': 0, 'max_value': 0, 'mean_nonzero': 0, 
                'low_coverage': 0, 'med_coverage': 0, 'high_coverage': 0, 'num_peaks': 0}

def find_local_maxima(density_map: np.ndarray, threshold: float = 0.01) -> list:
    """Find local maxima in density map (representing potential people)"""
    try:
        from scipy import ndimage
        # Use scipy if available, otherwise simple approach
        local_maxima = ndimage.maximum_filter(density_map, size=5) == density_map
        peaks = np.where((local_maxima) & (density_map > threshold))
        return list(zip(peaks[0], peaks[1]))
    except ImportError:
        # Fallback: simple peak detection
        peaks = []
        for i in range(2, density_map.shape[0]-2):
            for j in range(2, density_map.shape[1]-2):
                if (density_map[i,j] > threshold and 
                    density_map[i,j] > density_map[i-1:i+2, j-1:j+2].mean() * 1.5):
                    peaks.append((i, j))
        return peaks

def balanced_count_calibration(raw_count: float, analysis: dict) -> Tuple[float, str]:
    """
    Apply balanced calibration based on density map analysis

    Args:
        raw_count: Raw count from density summation
        analysis: Density map analysis results

    Returns:
        Tuple of (calibrated_count, reasoning)
    """
    try:
        total_sum = analysis['total_sum']
        max_value = analysis['max_value']
        num_peaks = analysis['num_peaks']
        med_coverage = analysis['med_coverage']

        logger.info(f"🔍 Analysis: sum={total_sum:.1f}, max={max_value:.3f}, peaks={num_peaks}, coverage={med_coverage:.3f}")

        # Multi-factor calibration
        if total_sum < 1.0:
            # Very low activation - likely no people or background noise
            calibrated = 0
            reasoning = "Very low activation - no people detected"

        elif max_value < 0.02 and total_sum < 10:
            # Low activation spread out - might be 1-2 people
            calibrated = max(1, num_peaks)
            reasoning = f"Low activation pattern - estimated {calibrated} people"

        elif num_peaks > 0 and num_peaks < 20:
            # Use peak-based counting for small to medium groups
            calibrated = max(num_peaks, int(total_sum * 0.1))
            reasoning = f"Peak-based counting - {num_peaks} peaks detected"

        elif med_coverage > 0.3:
            # High coverage - likely a crowd
            calibrated = int(total_sum * 0.4)  # Less aggressive scaling
            reasoning = "High coverage - crowd detected"

        else:
            # Medium case - moderate scaling
            calibrated = int(total_sum * 0.2)
            reasoning = "Medium activation - moderate scaling applied"

        # Apply reasonable bounds
        calibrated = max(0, min(calibrated, 1000))  # Cap at 1000 people max

        logger.info(f"📊 Calibration: {raw_count:.1f} → {calibrated} ({reasoning})")

        return float(calibrated), reasoning

    except Exception as e:
        logger.error(f"Calibration failed: {e}")
        # Fallback: conservative scaling
        fallback = max(0, int(raw_count * 0.1))
        return float(fallback), "Fallback calibration applied"

def get_count_from_density(density_map: np.ndarray, 
                          threshold: float = 0.005,  # Balanced threshold
                          apply_gaussian: bool = True,
                          sigma: float = 1.5,  # Moderate smoothing
                          use_calibration: bool = True) -> float:
    """
    Convert density map to crowd count with balanced calibration

    Args:
        density_map: 2D numpy array representing density map
        threshold: Minimum density value to consider
        apply_gaussian: Whether to apply Gaussian smoothing
        sigma: Standard deviation for Gaussian kernel
        use_calibration: Whether to use intelligent calibration

    Returns:
        Estimated crowd count as float
    """
    try:
        # Ensure 2D array
        if len(density_map.shape) > 2:
            density_map = np.squeeze(density_map)

        if len(density_map.shape) != 2:
            raise ValueError(f"Expected 2D density map, got shape: {density_map.shape}")

        original_sum = np.sum(density_map)
        logger.debug(f"Original density sum: {original_sum:.2f}")
        logger.debug(f"Density range: [{density_map.min():.4f}, {density_map.max():.4f}]")

        # Apply moderate Gaussian smoothing
        if apply_gaussian and sigma > 0:
            kernel_size = max(3, int(4 * sigma + 1))
            if kernel_size % 2 == 0:
                kernel_size += 1
            density_map = cv2.GaussianBlur(density_map, (kernel_size, kernel_size), sigma)

        # Apply threshold to remove noise
        density_map = np.maximum(density_map, 0)
        density_map[density_map < threshold] = 0

        # Calculate raw count
        raw_count = np.sum(density_map)

        if use_calibration:
            # Analyze density map
            analysis = analyze_density_map(density_map)

            # Apply balanced calibration
            final_count, reasoning = balanced_count_calibration(raw_count, analysis)

            logger.info(f"✅ Final result: {final_count} people ({reasoning})")
        else:
            final_count = raw_count
            logger.info(f"Raw count: {final_count}")

        return final_count

    except Exception as e:
        logger.error(f"Density to count conversion failed: {e}")
        return 0.0

def get_count_with_classification(density_map: np.ndarray, 
                                cls_logits: Optional[np.ndarray] = None,
                                bins: list = None) -> Tuple[float, Optional[int]]:
    """Get count using both density map and classification head"""
    density_count = get_count_from_density(density_map, use_calibration=True)

    classification_bin = None
    if cls_logits is not None:
        probs = torch.softmax(torch.from_numpy(cls_logits), dim=-1)
        classification_bin = torch.argmax(probs).item()
        logger.debug(f"Classification bin: {classification_bin}, confidence: {probs[classification_bin]:.3f}")

    return density_count, classification_bin

def postprocess_density_map(density_map: torch.Tensor,
                           original_size: Tuple[int, int],
                           apply_sigmoid: bool = False) -> np.ndarray:
    """Postprocess model output density map"""
    try:
        # Handle different input shapes
        if len(density_map.shape) == 4:
            density_map = density_map.squeeze(0).squeeze(0)
        elif len(density_map.shape) == 3:
            density_map = density_map.squeeze(0)

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

        return density_np

    except Exception as e:
        logger.error(f"Density map postprocessing failed: {e}")
        return np.zeros((128, 128), dtype=np.float32)

def visualize_density_map(density_map: np.ndarray, 
                         colormap: int = cv2.COLORMAP_JET,
                         normalize: bool = True) -> np.ndarray:
    """Create visualization of density map for debugging"""
    try:
        if normalize and density_map.max() > 0:
            normalized = (density_map / density_map.max() * 255).astype(np.uint8)
        else:
            normalized = np.clip(density_map * 255, 0, 255).astype(np.uint8)

        colored_heatmap = cv2.applyColorMap(normalized, colormap)
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
    'balanced_count_calibration',
    'analyze_density_map'
]
