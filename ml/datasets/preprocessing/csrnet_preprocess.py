"""
CSRNet Image Preprocessing Module

This module implements the EXACT preprocessing used in the original CSRNet paper.
Key points:
1. NO resizing - model accepts any resolution
2. Only ToTensor + ImageNet Normalization
3. Output density map is downsampled by factor of 8
"""

import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)


class CSRNetPreprocessor:
    """
    Preprocessor for CSRNet model following the original paper
    
    The original CSRNet paper uses:
    - No resizing (fully convolutional network)
    - ToTensor: Converts PIL Image [0, 255] to Tensor [0.0, 1.0]
    - Normalize: ImageNet mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    """
    
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],  # ImageNet mean
                std=[0.229, 0.224, 0.225]     # ImageNet std
            )
        ])
        logger.info("CSRNetPreprocessor initialized (no resizing, ImageNet normalization)")
    
    def preprocess(self, image):
        """
        Preprocess a PIL Image for CSRNet inference
        
        Args:
            image: PIL Image (RGB)
            
        Returns:
            torch.Tensor: Preprocessed image tensor [1, 3, H, W]
        """
        if not isinstance(image, Image.Image):
            raise TypeError(f"Expected PIL Image, got {type(image)}")
        
        # Ensure RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        original_size = image.size  # (W, H)
        logger.info(f"Input image size: {original_size[0]}x{original_size[1]}")
        
        # Apply transform: ToTensor + Normalize
        img_tensor = self.transform(image)
        
        # Add batch dimension
        img_tensor = img_tensor.unsqueeze(0)
        
        logger.info(f"Preprocessed tensor shape: {img_tensor.shape}")
        logger.info(f"Tensor value range: [{img_tensor.min():.3f}, {img_tensor.max():.3f}]")
        
        return img_tensor
    
    def preprocess_from_path(self, image_path):
        """
        Load and preprocess an image from file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            torch.Tensor: Preprocessed image tensor [1, 3, H, W]
        """
        image = Image.open(image_path).convert('RGB')
        return self.preprocess(image)
    
    def preprocess_from_bytes(self, image_bytes):
        """
        Load and preprocess an image from bytes
        
        Args:
            image_bytes: Image bytes (e.g., from file upload)
            
        Returns:
            torch.Tensor: Preprocessed image tensor [1, 3, H, W]
        """
        import io
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        return self.preprocess(image)
    
    def get_output_shape(self, input_shape):
        """
        Calculate output density map shape for given input
        
        CSRNet downsamples by factor of 8 due to 3 max pooling layers
        
        Args:
            input_shape: (H, W) or (B, C, H, W)
            
        Returns:
            tuple: Output density map shape
        """
        if len(input_shape) == 2:
            h, w = input_shape
            return (h // 8, w // 8)
        elif len(input_shape) == 4:
            b, c, h, w = input_shape
            return (b, 1, h // 8, w // 8)
        else:
            raise ValueError(f"Expected shape (H,W) or (B,C,H,W), got {input_shape}")


def get_csrnet_preprocessor():
    """Factory function to get CSRNet preprocessor"""
    return CSRNetPreprocessor()


# For backward compatibility
def preprocess_image(image):
    """
    Simple preprocessing function (backward compatible)
    
    Args:
        image: PIL Image
        
    Returns:
        torch.Tensor: Preprocessed tensor
    """
    preprocessor = CSRNetPreprocessor()
    return preprocessor.preprocess(image)
