import torch
import numpy as np
from PIL import Image
import torch.nn.functional as F

# BYPASS torchvision transforms - use custom implementation
class CustomTransforms:
    @staticmethod
    def Compose(transform_list):
        def compose_func(x):
            for transform in transform_list:
                x = transform(x)
            return x
        return compose_func
    
    @staticmethod
    def ToTensor():
        def to_tensor(pic):
            if isinstance(pic, Image.Image):
                pic = np.array(pic)
            if pic.ndim == 2:  # Grayscale
                pic = pic[..., None]
            pic = pic.transpose(2, 0, 1)  # HWC to CHW
            return torch.from_numpy(pic).float() / 255.0
        return to_tensor
    
    @staticmethod
    def Normalize(mean, std):
        def normalize(tensor):
            mean_t = torch.tensor(mean).view(-1, 1, 1)
            std_t = torch.tensor(std).view(-1, 1, 1)
            return (tensor - mean_t) / std_t
        return normalize
    
    @staticmethod
    def Resize(size):
        def resize(tensor):
            if isinstance(size, int):
                h, w = size, size
            else:
                h, w = size
            return F.interpolate(tensor.unsqueeze(0), size=(h, w), mode='bilinear', align_corners=False).squeeze(0)
        return resize

# Use custom transforms instead of torchvision
transforms = CustomTransforms()

def preprocess_frame(image: Image.Image):
    """Preprocess image for crowd counting model"""
    try:
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Define preprocessing pipeline
        preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Apply preprocessing
        tensor = preprocess(image)
        
        # Add batch dimension
        tensor = tensor.unsqueeze(0)
        
        return tensor
        
    except Exception as e:
        raise RuntimeError(f"Preprocessing failed: {e}")

# Export function
__all__ = ['preprocess_frame']
