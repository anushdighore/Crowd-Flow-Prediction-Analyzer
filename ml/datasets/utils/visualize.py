import cv2
import numpy as np
import base64
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def generate_heatmap_overlay(density_map: np.ndarray, 
                           original_image: np.ndarray, 
                           alpha: float = 0.5,
                           colormap: int = cv2.COLORMAP_JET,
                           quality: int = 90) -> str:
    """
    Generate heatmap overlay of density map on original image and return as base64 string

    Args:
        density_map: 2D numpy array (H, W) - model output density map
        original_image: OpenCV BGR image (H, W, 3) - original input image
        alpha: Blending weight (0.0-1.0) between original and heatmap
        colormap: OpenCV colormap constant (default: COLORMAP_JET)
        quality: JPEG compression quality (0-100, default: 90)

    Returns:
        Base64 encoded string with "data:image/jpeg;base64," prefix

    Raises:
        ValueError: If input arrays are invalid or alpha is out of range
        RuntimeError: If image processing fails
    """
    try:
        # Validate inputs
        if not isinstance(density_map, np.ndarray) or len(density_map.shape) != 2:
            raise ValueError(f"density_map must be 2D numpy array, got shape: {density_map.shape}")

        if not isinstance(original_image, np.ndarray) or len(original_image.shape) != 3:
            raise ValueError(f"original_image must be 3D numpy array, got shape: {original_image.shape}")

        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha must be between 0.0 and 1.0, got: {alpha}")

        logger.debug(f"Input shapes - density_map: {density_map.shape}, original_image: {original_image.shape}")

        # Ensure density map is non-negative and finite
        density_map = np.nan_to_num(density_map, nan=0.0, posinf=0.0, neginf=0.0)
        density_map = np.maximum(density_map, 0.0)

        # Get target dimensions from original image
        img_height, img_width = original_image.shape[:2]

        # Resize density map to match original image dimensions if needed
        if density_map.shape != (img_height, img_width):
            logger.debug(f"Resizing density map from {density_map.shape} to ({img_height}, {img_width})")
            density_map_resized = cv2.resize(
                density_map, 
                (img_width, img_height), 
                interpolation=cv2.INTER_LINEAR
            )
        else:
            density_map_resized = density_map.copy()

        # Normalize density map to [0, 255] range
        if density_map_resized.max() > density_map_resized.min():
            normalized = ((density_map_resized - density_map_resized.min()) / 
                         (density_map_resized.max() - density_map_resized.min()) * 255.0)
        else:
            # Handle case where all values are the same
            normalized = np.zeros_like(density_map_resized)

        # Convert to uint8
        normalized_uint8 = normalized.astype(np.uint8)

        logger.debug(f"Normalized density range: [{normalized_uint8.min()}, {normalized_uint8.max()}]")

        # Apply colormap to create heatmap
        heatmap_colored = cv2.applyColorMap(normalized_uint8, colormap)

        # Ensure original image is uint8
        if original_image.dtype != np.uint8:
            if original_image.max() <= 1.0:
                # Assume normalized image [0, 1]
                original_uint8 = (original_image * 255.0).astype(np.uint8)
            else:
                # Assume regular image values
                original_uint8 = np.clip(original_image, 0, 255).astype(np.uint8)
        else:
            original_uint8 = original_image.copy()

        # Blend images using weighted addition
        blended = cv2.addWeighted(
            original_uint8, 1.0 - alpha,
            heatmap_colored, alpha,
            0
        )

        logger.debug(f"Blended image shape: {blended.shape}, dtype: {blended.dtype}")

        # Encode as JPEG
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, encoded_img = cv2.imencode('.jpg', blended, encode_params)

        if not success:
            raise RuntimeError("Failed to encode image as JPEG")

        # Convert to base64 string
        img_bytes = encoded_img.tobytes()
        base64_str = base64.b64encode(img_bytes).decode('utf-8')

        # Add data URL prefix
        data_url = f"data:image/jpeg;base64,{base64_str}"

        logger.info(f"✅ Generated heatmap overlay: {len(data_url)} characters")

        return data_url

    except Exception as e:
        logger.error(f"Failed to generate heatmap overlay: {e}")
        raise RuntimeError(f"Heatmap generation failed: {str(e)}")

def generate_pure_heatmap(density_map: np.ndarray,
                         colormap: int = cv2.COLORMAP_JET,
                         size: Optional[Tuple[int, int]] = None,
                         quality: int = 90) -> str:
    """
    Generate pure heatmap visualization without overlay

    Args:
        density_map: 2D numpy array (H, W) - model output density map
        colormap: OpenCV colormap constant (default: COLORMAP_JET)
        size: Optional target size (width, height) for resizing
        quality: JPEG compression quality (0-100, default: 90)

    Returns:
        Base64 encoded string with "data:image/jpeg;base64," prefix
    """
    try:
        # Validate input
        if not isinstance(density_map, np.ndarray) or len(density_map.shape) != 2:
            raise ValueError(f"density_map must be 2D numpy array, got shape: {density_map.shape}")

        # Clean density map
        density_map = np.nan_to_num(density_map, nan=0.0, posinf=0.0, neginf=0.0)
        density_map = np.maximum(density_map, 0.0)

        # Resize if requested
        if size is not None:
            width, height = size
            density_map = cv2.resize(density_map, (width, height), interpolation=cv2.INTER_LINEAR)

        # Normalize to [0, 255]
        if density_map.max() > density_map.min():
            normalized = ((density_map - density_map.min()) / 
                         (density_map.max() - density_map.min()) * 255.0)
        else:
            normalized = np.zeros_like(density_map)

        normalized_uint8 = normalized.astype(np.uint8)

        # Apply colormap
        heatmap_colored = cv2.applyColorMap(normalized_uint8, colormap)

        # Encode as JPEG
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, encoded_img = cv2.imencode('.jpg', heatmap_colored, encode_params)

        if not success:
            raise RuntimeError("Failed to encode heatmap as JPEG")

        # Convert to base64
        img_bytes = encoded_img.tobytes()
        base64_str = base64.b64encode(img_bytes).decode('utf-8')

        return f"data:image/jpeg;base64,{base64_str}"

    except Exception as e:
        logger.error(f"Failed to generate pure heatmap: {e}")
        raise RuntimeError(f"Pure heatmap generation failed: {str(e)}")

def create_density_statistics_overlay(density_map: np.ndarray,
                                    original_image: np.ndarray,
                                    stats: dict,
                                    alpha: float = 0.3) -> str:
    """
    Create visualization with density statistics overlay

    Args:
        density_map: 2D numpy array - density map
        original_image: OpenCV BGR image
        stats: Dictionary with statistics (from get_density_statistics)
        alpha: Blending weight for overlay

    Returns:
        Base64 encoded image string
    """
    try:
        # Generate base heatmap
        base_overlay = generate_heatmap_overlay(
            density_map, original_image, alpha, cv2.COLORMAP_VIRIDIS
        )

        # For now, return the base overlay
        # In a full implementation, you could add text overlays with statistics
        logger.info(f"Generated statistics overlay with {stats.get('total_count', 0)} total count")

        return base_overlay

    except Exception as e:
        logger.error(f"Failed to create statistics overlay: {e}")
        raise RuntimeError(f"Statistics overlay failed: {str(e)}")

def validate_colormap(colormap_name: str) -> int:
    """
    Validate and convert colormap name to OpenCV constant

    Args:
        colormap_name: String name of colormap

    Returns:
        OpenCV colormap constant
    """
    colormap_dict = {
        'jet': cv2.COLORMAP_JET,
        'hot': cv2.COLORMAP_HOT,
        'cool': cv2.COLORMAP_COOL,
        'viridis': cv2.COLORMAP_VIRIDIS,
        'plasma': cv2.COLORMAP_PLASMA,
        'magma': cv2.COLORMAP_MAGMA,
        'inferno': cv2.COLORMAP_INFERNO,
        'rainbow': cv2.COLORMAP_RAINBOW,
        'ocean': cv2.COLORMAP_OCEAN,
        'summer': cv2.COLORMAP_SUMMER,
        'spring': cv2.COLORMAP_SPRING,
        'winter': cv2.COLORMAP_WINTER
    }

    colormap_name_lower = colormap_name.lower()
    if colormap_name_lower in colormap_dict:
        return colormap_dict[colormap_name_lower]
    else:
        logger.warning(f"Unknown colormap '{colormap_name}', using JET as default")
        return cv2.COLORMAP_JET

# Export main functions
__all__ = [
    'generate_heatmap_overlay',
    'generate_pure_heatmap', 
    'create_density_statistics_overlay',
    'validate_colormap'
]
