"""
Inference Engine - Execute model inference

Handles:
- Single image inference
- Batch inference  
- Stream inference (real-time)
- Performance tracking
- Result formatting

Works with DeviceManager and ModelManager
"""

import torch
import torch.nn as nn
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
import time
from pathlib import Path

from .device_manager import DeviceManager, get_device_manager
from .model_manager import ModelManager, get_model_manager

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Executes model inference with performance tracking"""
    
    def __init__(
        self,
        model_manager: Optional[ModelManager] = None,
        device_manager: Optional[DeviceManager] = None
    ):
        """
        Initialize InferenceEngine
        
        Args:
            model_manager: ModelManager instance
            device_manager: DeviceManager instance
        """
        self.model_manager = model_manager or get_model_manager()
        self.device_manager = device_manager or get_device_manager()
        
        # Performance statistics
        self.stats = {
            'total_inferences': 0,
            'total_time': 0.0,
            'model_stats': {}  # Per-model statistics
        }
        
        logger.info("Inference Engine initialized")
    
    def infer_single(
        self,
        image: np.ndarray,
        model_name: str,
        return_density_map: bool = True
    ) -> Dict[str, Any]:
        """
        Single image inference
        
        Args:
            image: Input image (numpy array, RGB, HWC format)
            model_name: Model identifier ('csrnet', 'tmtb')
            return_density_map: Include density map in output
            
        Returns:
            Result dictionary with count, density map, etc.
        """
        # Get model
        model = self.model_manager.get_model(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not loaded. Call model_manager.load_model() first.")
        
        # Get config
        config = self.model_manager.configs.get(model_name)
        if config is None:
            raise ValueError(f"Config for {model_name} not found")
        
        # Get device
        device = self.model_manager.metadata[model_name]['device']
        
        # Preprocess
        input_tensor = self._preprocess_image(image, model_name, device)
        
        # Inference
        start_time = time.time()
        
        model.eval()
        with torch.no_grad():
            density_map = model(input_tensor)
            
            # Synchronize if GPU
            if device == 'cuda':
                torch.cuda.synchronize()
        
        inference_time = time.time() - start_time
        
        # Post-process
        result = self._postprocess_output(
            density_map,
            model_name,
            config,
            inference_time,
            return_density_map
        )
        
        # Update statistics
        self._update_stats(model_name, inference_time)
        
        return result
    
    def infer_batch(
        self,
        images: List[np.ndarray],
        model_name: str,
        return_density_maps: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Batch inference
        
        Args:
            images: List of input images
            model_name: Model identifier
            return_density_maps: Include density maps in output
            
        Returns:
            List of result dictionaries
        """
        # Get model
        model = self.model_manager.get_model(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not loaded")
        
        # Get config
        config = self.model_manager.configs.get(model_name)
        batch_size = config['inference']['batch_size']
        device = self.model_manager.metadata[model_name]['device']
        
        results = []
        
        # Process in batches
        for i in range(0, len(images), batch_size):
            batch_images = images[i:i+batch_size]
            
            # Preprocess batch
            batch_tensors = []
            for img in batch_images:
                tensor = self._preprocess_image(img, model_name, device)
                batch_tensors.append(tensor)
            
            # Stack into batch
            batch_input = torch.cat(batch_tensors, dim=0)
            
            # Inference
            start_time = time.time()
            
            model.eval()
            with torch.no_grad():
                batch_density_maps = model(batch_input)
                
                if device == 'cuda':
                    torch.cuda.synchronize()
            
            inference_time = time.time() - start_time
            
            # Post-process each result in batch
            for j in range(batch_density_maps.shape[0]):
                density_map = batch_density_maps[j:j+1]  # Keep batch dim
                
                result = self._postprocess_output(
                    density_map,
                    model_name,
                    config,
                    inference_time / batch_density_maps.shape[0],  # Per-image time
                    return_density_maps
                )
                
                results.append(result)
            
            # Update statistics
            self._update_stats(model_name, inference_time, count=batch_density_maps.shape[0])
        
        return results
    
    def infer_stream(
        self,
        frame_generator,
        model_name: str,
        callback=None,
        max_fps: Optional[int] = None
    ):
        """
        Stream inference (for video/webcam)
        
        Args:
            frame_generator: Generator yielding frames
            model_name: Model identifier
            callback: Callback function(frame, result) called for each result
            max_fps: Maximum FPS (rate limiting)
        """
        # Get model
        model = self.model_manager.get_model(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not loaded")
        
        # Get config
        config = self.model_manager.configs.get(model_name)
        device = self.model_manager.metadata[model_name]['device']
        
        # FPS control
        if max_fps is None:
            max_fps = config['realtime']['max_fps']
        
        min_frame_time = 1.0 / max_fps if max_fps > 0 else 0
        
        frame_count = 0
        total_time = 0.0
        
        logger.info(f"Starting stream inference with {model_name} (max {max_fps} FPS)")
        
        try:
            for frame in frame_generator:
                loop_start = time.time()
                
                # Inference
                result = self.infer_single(frame, model_name, return_density_map=False)
                
                # Callback
                if callback:
                    callback(frame, result)
                
                # FPS limiting
                elapsed = time.time() - loop_start
                if elapsed < min_frame_time:
                    time.sleep(min_frame_time - elapsed)
                
                frame_count += 1
                total_time += elapsed
                
                # Log FPS every 30 frames
                if frame_count % 30 == 0:
                    avg_fps = frame_count / total_time
                    logger.info(f"Processed {frame_count} frames, avg FPS: {avg_fps:.1f}")
        
        except KeyboardInterrupt:
            logger.info("Stream inference interrupted by user")
        
        except Exception as e:
            logger.error(f"Stream inference error: {e}")
            raise
        
        finally:
            logger.info(f"Stream inference complete: {frame_count} frames")
    
    def _preprocess_image(
        self,
        image: np.ndarray,
        model_name: str,
        device: str
    ) -> torch.Tensor:
        """
        Preprocess image for model inference
        
        Args:
            image: Input image (numpy array, RGB, HWC)
            model_name: Model identifier
            device: Target device
            
        Returns:
            Preprocessed tensor
        """
        if model_name == 'csrnet':
            return self._preprocess_csrnet(image, device)
        elif model_name == 'tmtb':
            return self._preprocess_tmtb(image, device)
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    def _preprocess_csrnet(
        self,
        image: np.ndarray,
        device: str
    ) -> torch.Tensor:
        """Preprocess for CSRNet"""
        # Use existing CSRNet preprocessor
        from preprocessing import CSRNetPreprocessor
        
        preprocessor = CSRNetPreprocessor()
        
        # Convert numpy to PIL if needed
        from PIL import Image
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        tensor = preprocessor.preprocess(image)
        tensor = tensor.to(device)
        
        return tensor
    
    def _preprocess_tmtb(
        self,
        image: np.ndarray,
        device: str
    ) -> torch.Tensor:
        """Preprocess for TMTB (placeholder)"""
        raise NotImplementedError("TMTB preprocessing will be implemented later")
    
    def _postprocess_output(
        self,
        density_map: torch.Tensor,
        model_name: str,
        config: Dict[str, Any],
        inference_time: float,
        return_density_map: bool
    ) -> Dict[str, Any]:
        """
        Post-process model output
        
        Args:
            density_map: Model output tensor
            model_name: Model identifier
            config: Model config
            inference_time: Inference time in seconds
            return_density_map: Include density map in output
            
        Returns:
            Result dictionary
        """
        # Extract count
        count = density_map.sum().item()
        
        # Apply scaling factor
        scaling_factor = config['postprocessing']['count_scaling_factor']
        count = count * scaling_factor
        
        # Build result
        result = {
            'model': model_name,
            'count': round(count, 2),
            'count_int': int(round(count)),
            'inference_time_ms': round(inference_time * 1000, 2),
            'density_map_shape': list(density_map.shape),
        }
        
        # Include density map if requested
        if return_density_map:
            density_map_np = density_map.squeeze().cpu().numpy()
            result['density_map'] = density_map_np
        
        # Log if enabled
        if config['logging']['log_inference_time']:
            logger.debug(f"{model_name} inference: {result['count_int']} people in {result['inference_time_ms']}ms")
        
        return result
    
    def _update_stats(self, model_name: str, time: float, count: int = 1):
        """Update performance statistics"""
        self.stats['total_inferences'] += count
        self.stats['total_time'] += time
        
        if model_name not in self.stats['model_stats']:
            self.stats['model_stats'][model_name] = {
                'inferences': 0,
                'total_time': 0.0,
                'avg_time': 0.0
            }
        
        model_stats = self.stats['model_stats'][model_name]
        model_stats['inferences'] += count
        model_stats['total_time'] += time
        model_stats['avg_time'] = model_stats['total_time'] / model_stats['inferences']
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = self.stats.copy()
        
        if stats['total_inferences'] > 0:
            stats['avg_time'] = stats['total_time'] / stats['total_inferences']
            stats['avg_fps'] = stats['total_inferences'] / stats['total_time']
        else:
            stats['avg_time'] = 0.0
            stats['avg_fps'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.stats = {
            'total_inferences': 0,
            'total_time': 0.0,
            'model_stats': {}
        }
        logger.info("Statistics reset")


# Singleton instance
_inference_engine_instance: Optional[InferenceEngine] = None


def get_inference_engine(
    model_manager: Optional[ModelManager] = None,
    device_manager: Optional[DeviceManager] = None
) -> InferenceEngine:
    """
    Get singleton InferenceEngine instance
    
    Args:
        model_manager: ModelManager instance (only used on first call)
        device_manager: DeviceManager instance (only used on first call)
        
    Returns:
        InferenceEngine instance
    """
    global _inference_engine_instance
    
    if _inference_engine_instance is None:
        _inference_engine_instance = InferenceEngine(model_manager, device_manager)
    
    return _inference_engine_instance
