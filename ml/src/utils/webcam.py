import cv2
import numpy as np
import logging
from typing import Optional, Tuple
import time

logger = logging.getLogger(__name__)


class WebcamCapture:
    """
    Webcam capture handler with preprocessing capabilities
    """
    
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """
        Initialize webcam capture
        
        Args:
            camera_id: Camera device ID (default: 0 for primary webcam)
            width: Frame width
            height: Frame height
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.is_opened = False
        
    def open(self) -> bool:
        """Open webcam connection"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                return False
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Set FPS (if supported)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_opened = True
            logger.info(f"✅ Webcam {self.camera_id} opened successfully ({self.width}x{self.height})")
            return True
            
        except Exception as e:
            logger.error(f"Error opening webcam: {e}")
            return False
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read a single frame from webcam
        
        Returns:
            Frame as numpy array (BGR format) or None if failed
        """
        if not self.is_opened or self.cap is None:
            logger.warning("Webcam not opened")
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            logger.warning("Failed to read frame")
            return None
        
        return frame
    
    def release(self):
        """Release webcam resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            logger.info("📹 Webcam released")
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()


def preprocess_webcam_frame(frame: np.ndarray, target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
    """
    Preprocess webcam frame for crowd counting
    
    Args:
        frame: OpenCV frame (BGR format)
        target_size: Optional target size (width, height) for resizing
        
    Returns:
        Preprocessed frame
    """
    try:
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize if target size specified
        if target_size is not None:
            frame_rgb = cv2.resize(frame_rgb, target_size, interpolation=cv2.INTER_LINEAR)
        
        return frame_rgb
        
    except Exception as e:
        logger.error(f"Error preprocessing frame: {e}")
        return frame


def draw_count_overlay(frame: np.ndarray, count: int, fps: Optional[float] = None, 
                       additional_info: Optional[dict] = None) -> np.ndarray:
    """
    Draw crowd count and additional information overlay on frame
    
    Args:
        frame: OpenCV frame (BGR format)
        count: Crowd count to display
        fps: Frames per second (optional)
        additional_info: Additional information to display (optional)
        
    Returns:
        Frame with overlay
    """
    try:
        # Create a copy to avoid modifying original
        overlay_frame = frame.copy()
        
        # Define overlay parameters
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        font_thickness = 2
        text_color = (0, 255, 0)  # Green
        bg_color = (0, 0, 0)  # Black background
        padding = 10
        
        # Main count text
        count_text = f"Count: {count}"
        (text_width, text_height), baseline = cv2.getTextSize(count_text, font, font_scale, font_thickness)
        
        # Draw background rectangle
        cv2.rectangle(overlay_frame, 
                     (padding, padding), 
                     (padding + text_width + padding, padding + text_height + padding),
                     bg_color, -1)
        
        # Draw count text
        cv2.putText(overlay_frame, count_text,
                   (padding + 5, padding + text_height),
                   font, font_scale, text_color, font_thickness)
        
        y_offset = padding + text_height + padding + 10
        
        # Draw FPS if provided
        if fps is not None:
            fps_text = f"FPS: {fps:.1f}"
            font_scale_small = 0.6
            font_thickness_small = 1
            
            (fps_width, fps_height), _ = cv2.getTextSize(fps_text, font, font_scale_small, font_thickness_small)
            
            cv2.rectangle(overlay_frame,
                         (padding, y_offset),
                         (padding + fps_width + padding, y_offset + fps_height + 5),
                         bg_color, -1)
            
            cv2.putText(overlay_frame, fps_text,
                       (padding + 5, y_offset + fps_height),
                       font, font_scale_small, (255, 255, 0), font_thickness_small)
            
            y_offset += fps_height + 15
        
        # Draw additional info if provided
        if additional_info:
            font_scale_info = 0.5
            font_thickness_info = 1
            
            for key, value in additional_info.items():
                info_text = f"{key}: {value}"
                (info_width, info_height), _ = cv2.getTextSize(info_text, font, font_scale_info, font_thickness_info)
                
                cv2.rectangle(overlay_frame,
                             (padding, y_offset),
                             (padding + info_width + padding, y_offset + info_height + 5),
                             bg_color, -1)
                
                cv2.putText(overlay_frame, info_text,
                           (padding + 5, y_offset + info_height),
                           font, font_scale_info, (200, 200, 200), font_thickness_info)
                
                y_offset += info_height + 10
        
        return overlay_frame
        
    except Exception as e:
        logger.error(f"Error drawing overlay: {e}")
        return frame


def save_frame(frame: np.ndarray, filename: str) -> bool:
    """
    Save frame to disk
    
    Args:
        frame: OpenCV frame
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cv2.imwrite(filename, frame)
        logger.info(f"💾 Frame saved to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving frame: {e}")
        return False


class FPSCounter:
    """Simple FPS counter"""
    
    def __init__(self, window_size: int = 30):
        """
        Initialize FPS counter
        
        Args:
            window_size: Number of frames to average over
        """
        self.window_size = window_size
        self.frame_times = []
        self.last_time = time.time()
    
    def update(self) -> float:
        """
        Update FPS counter with current frame
        
        Returns:
            Current FPS
        """
        current_time = time.time()
        frame_time = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(frame_time)
        
        # Keep only recent frames
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        
        # Calculate average FPS
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        return fps
    
    def reset(self):
        """Reset FPS counter"""
        self.frame_times = []
        self.last_time = time.time()


# Export main classes and functions
__all__ = [
    'WebcamCapture',
    'preprocess_webcam_frame',
    'draw_count_overlay',
    'save_frame',
    'FPSCounter'
]
