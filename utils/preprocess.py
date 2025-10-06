from __future__ import annotations

import torch
import numpy as np
from PIL import Image
import torch.nn.functional as F
from typing import Any, Callable, Iterable


def _ensure_pil_rgb(image: Any) -> Image.Image:
    """Convert numpy/OpenCV images to PIL RGB."""
    if isinstance(image, Image.Image):
        return image.convert('RGB') if image.mode != 'RGB' else image

    if isinstance(image, np.ndarray):
        if image.ndim == 2:
            pil_image = Image.fromarray(image)
            return pil_image.convert('RGB')

        if image.ndim == 3:
            if image.shape[2] == 3:
                # Assume BGR (OpenCV default) and flip channels
                rgb_array = image[:, :, ::-1].copy()
                return Image.fromarray(rgb_array)
            if image.shape[2] == 4:
                rgb_array = image[:, :, :3][:, :, ::-1].copy()
                return Image.fromarray(rgb_array)
        raise ValueError(f"Unsupported numpy image shape: {image.shape}")

    raise TypeError(f"Unsupported image type: {type(image)}")

# BYPASS torchvision transforms - use custom implementation
class CustomTransforms:
    @staticmethod
    def Compose(transform_list: Iterable[Callable[[torch.Tensor], torch.Tensor]]) -> Callable[[torch.Tensor], torch.Tensor]:
        def compose_func(x: torch.Tensor) -> torch.Tensor:
            for transform in transform_list:
                x = transform(x)
            return x
        return compose_func
    
    @staticmethod
    def ToTensor() -> Callable[[Any], torch.Tensor]:
        def to_tensor(pic: Any) -> torch.Tensor:
            if isinstance(pic, Image.Image):
                pic = np.array(pic)
            if pic.ndim == 2:  # Grayscale
                pic = pic[..., None]
            pic = pic.transpose(2, 0, 1)  # HWC to CHW
            return torch.from_numpy(pic).float() / 255.0
        return to_tensor
    
    @staticmethod
    def Normalize(mean: Iterable[float], std: Iterable[float]) -> Callable[[torch.Tensor], torch.Tensor]:
        def normalize(tensor: torch.Tensor) -> torch.Tensor:
            mean_t = torch.tensor(mean).view(-1, 1, 1)
            std_t = torch.tensor(std).view(-1, 1, 1)
            return (tensor - mean_t) / std_t
        return normalize
    
    @staticmethod
    def Resize(size: Any) -> Callable[[torch.Tensor], torch.Tensor]:
        def resize(tensor: torch.Tensor) -> torch.Tensor:
            if isinstance(size, int):
                h, w = size, size
            else:
                h, w = size
            return F.interpolate(tensor.unsqueeze(0), size=(h, w), mode='bilinear', align_corners=False).squeeze(0)
        return resize

# Use custom transforms instead of torchvision
transforms = CustomTransforms()

def preprocess_frame(image: Any, max_long_edge: int = 1536) -> torch.Tensor:
    """Preprocess image for crowd counting model.

    Args:
        image: Input image in PIL, numpy (HWC, BGR), or grayscale formats.
        max_long_edge: Maximum size for the image's longest edge. If the
            provided image exceeds this, it will be downscaled while preserving
            aspect ratio to accelerate inference.

    Returns:
        torch.Tensor: Normalized image tensor in BCHW format (batch dimension
        included).
    """
    try:
        # Ensure we work with a PIL RGB image regardless of input
        image = _ensure_pil_rgb(image)

        if max_long_edge is not None and max_long_edge > 0:
            width, height = image.size
            long_edge = max(width, height)
            if long_edge > max_long_edge:
                scale = max_long_edge / long_edge
                new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
                image = image.resize(new_size, Image.BICUBIC)
    
        # Define preprocessing pipeline
        preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Apply preprocessing, add batch dimension and return
        tensor = preprocess(image).unsqueeze(0)

        return tensor
        
    except Exception as e:
        raise RuntimeError(f"Preprocessing failed: {e}")

# Export function
__all__ = ['preprocess_frame']
