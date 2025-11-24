"""
Pedestrian Tracking Service
Wraps tracker_ped.py functionality with optional homography support
"""
import cv2
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging
from collections import defaultdict
import sys

logger = logging.getLogger(__name__)

# Import tracker_ped and visualizer
try:
    from v3Updates.tracker_ped import CrowdDensityEstimation
    logger.info("✅ Imported tracker_ped.CrowdDensityEstimation")
except ImportError as e:
    logger.warning(f"⚠️ Could not import tracker_ped: {e}")
    CrowdDensityEstimation = None

try:
    from models.v3_analyzer import PedestrianVisualizer
    logger.info("✅ Imported PedestrianVisualizer")
except ImportError as e:
    logger.warning(f"⚠️ Could not import PedestrianVisualizer: {e}")
    PedestrianVisualizer = None


class PedestrianTracker:
    """
    Wrapper around tracker_ped.CrowdDensityEstimation for pedestrian tracking
    Provides optional homography-based world coordinate transformation
    """
    
    def __init__(
        self,
        model_path: str = 'yolov8n.pt',
        conf_threshold: float = 0.3,
        iou_threshold: float = 0.5,
        device: str = 'cuda',
        trajectory_max_points: int = 30,
        trajectory_max_distance_cm: float = 2.0,
        enable_visualization: bool = True,
    ):
        """
        Initialize pedestrian tracker
        
        Args:
            model_path: Path to YOLO model weights
            conf_threshold: Confidence threshold for detections
            iou_threshold: IOU threshold for tracking
            device: 'cuda' or 'cpu'
            trajectory_max_points: Maximum trajectory points to display (configurable per frame)
            trajectory_max_distance_cm: Max real-world distance in cm
            enable_visualization: Enable trajectory visualization
        """
        if CrowdDensityEstimation is None:
            raise RuntimeError("tracker_ped module not available")
        
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        
        # Initialize tracker
        self.tracker = CrowdDensityEstimation(
            model_path=model_path,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold
        )
        logger.info(f"✅ PedestrianTracker initialized with model: {model_path}")
        
        # Homography matrix for world coordinate transformation (optional)
        self.homography_matrix = None
        self.use_world_coords = False
        
        # Visualization settings
        self.trajectory_max_points = trajectory_max_points
        self.trajectory_max_distance_cm = trajectory_max_distance_cm
        self.visualizer = None
        
        if enable_visualization and PedestrianVisualizer:
            self.visualizer = PedestrianVisualizer(
                trajectory_max_points=trajectory_max_points,
                trajectory_max_distance_cm=trajectory_max_distance_cm
            )
            logger.info("✅ Visualization enabled")
        
    def set_homography(
        self,
        image_points: List[List[float]],
        world_points: List[List[float]]
    ) -> bool:
        """
        Set homography matrix for world coordinate transformation
        
        Args:
            image_points: 4 image coordinate points [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            world_points: 4 world coordinate points in same order
        
        Returns:
            True if homography set successfully, False otherwise
        """
        try:
            if len(image_points) < 4 or len(world_points) < 4:
                logger.error("Need at least 4 point correspondences")
                return False
            
            self.tracker.set_homography_matrix(image_points, world_points)
            self.homography_matrix = self.tracker.homography_matrix
            self.use_world_coords = True
            logger.info("✅ Homography matrix set successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set homography: {e}")
            return False
    
    def process_frame(
        self,
        frame: np.ndarray,
        frame_number: int = 0,
        max_trajectory_points: Optional[int] = None,
        annotate: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a single frame for pedestrian tracking with optional visualization
        
        Args:
            frame: Input frame (BGR image)
            frame_number: Frame index
            max_trajectory_points: Override default max trajectory points
            annotate: Whether to annotate frame with visualizations
        
        Returns:
            Dict containing:
                - frame_number: Frame index
                - count: Current pedestrian count
                - unique_count: Total unique pedestrians seen
                - trajectories: Dict of {track_id: [(x,y), ...]}
                - annotated_frame: Frame with boxes, trajectories, and count badge
                - use_world_coords: Whether world coordinates are used
        """
        try:
            # Extract tracks
            results, resized_frame = self.tracker.extract_tracks(frame)
            
            # Get current counts
            current_count = len(results[0].boxes.id) if results[0].boxes.id is not None else 0
            
            # Update trajectories
            self.tracker.update_trajectories(results, frame_number)
            
            # Extract additional tracking data
            trajectories = dict(self.tracker.track_history)
            
            # Build result
            result = {
                'frame_number': frame_number,
                'count': current_count,
                'unique_count': len(self.tracker.unique_persons),
                'trajectories': trajectories,
                'use_world_coords': self.use_world_coords
            }
            
            # Annotate frame if visualizer available and requested
            if annotate and self.visualizer and results[0].boxes.id is not None:
                annotated_frame = self.visualizer.annotate_frame(
                    resized_frame.copy(),
                    results,
                    trajectories,
                    len(self.tracker.unique_persons),
                    current_count,
                    self.homography_matrix,
                    max_trajectory_points or self.trajectory_max_points,
                    badge_position="bottom-right"
                )
                result['annotated_frame'] = annotated_frame
            else:
                result['annotated_frame'] = resized_frame
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return {
                'error': str(e),
                'frame_number': frame_number,
                'annotated_frame': None
            }
    
    def save_trajectories(self, output_path: str) -> bool:
        """
        Save trajectory data to CSV
        
        Args:
            output_path: Path to save CSV file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.tracker.save_trajectories(output_path)
            logger.info(f"✅ Trajectories saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save trajectories: {e}")
            return False
    
    def get_trajectory_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get trajectory data as pandas DataFrame
        
        Returns:
            DataFrame with columns: id, frame, x, y (or None if empty)
        """
        try:
            trajectory_data = []
            for person_id, positions in self.tracker.track_history.items():
                for frame_idx, pos in enumerate(positions):
                    trajectory_data.append({
                        'id': person_id,
                        'frame': frame_idx,
                        'x': pos[0] if isinstance(pos, tuple) else pos,
                        'y': pos[1] if isinstance(pos, tuple) else 0,
                    })
            
            if not trajectory_data:
                return None
            
            return pd.DataFrame(trajectory_data)
        except Exception as e:
            logger.error(f"Error getting trajectory dataframe: {e}")
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get tracking metrics
        
        Returns:
            Dict with:
                - total_unique_persons: Total pedestrians tracked
                - current_count: Pedestrians in current frame
                - trajectory_count: Number of trajectory data points
                - frames_processed: Total frames processed
        """
        trajectory_points = sum(
            len(positions) 
            for positions in self.tracker.track_history.values()
        )
        
        return {
            'total_unique_persons': len(self.tracker.unique_persons),
            'current_count': 0,  # Would need last frame data
            'trajectory_points': trajectory_points,
            'total_tracks': len(self.tracker.track_history)
        }
    
    def reset(self):
        """Reset tracker state"""
        try:
            self.tracker.track_history.clear()
            self.tracker.unique_persons.clear()
            self.tracker.track_colors.clear()
            logger.info("✅ Tracker reset")
        except Exception as e:
            logger.error(f"Error resetting tracker: {e}")


class PedestrianTrackingPipeline:
    """
    Full pipeline for processing video with pedestrian tracking
    """
    
    def __init__(self, model_path: str = 'yolov8n.pt', device: str = 'cuda'):
        """Initialize tracking pipeline"""
        self.tracker = PedestrianTracker(model_path=model_path, device=device)
        self.frames_processed = 0
        self.output_video_path = None
        self.video_writer = None
    
    def process_video(
        self,
        video_path: str,
        output_path: str,
        homography_data: Optional[Dict[str, Any]] = None,
        frame_skip: int = 1
    ) -> Dict[str, Any]:
        """
        Process entire video file
        
        Args:
            video_path: Path to input video
            output_path: Path to save processed video
            homography_data: Optional dict with 'image_points' and 'world_points'
            frame_skip: Process every Nth frame
        
        Returns:
            Dict with processing results
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {'error': 'Could not open video file'}
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Set homography if provided
            if homography_data:
                self.tracker.set_homography(
                    homography_data.get('image_points', []),
                    homography_data.get('world_points', [])
                )
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                output_path, fourcc, fps, (width, height)
            )
            
            self.output_video_path = output_path
            self.frames_processed = 0
            frame_number = 0
            
            # Process frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_number % frame_skip == 0:
                    result = self.tracker.process_frame(frame, frame_number)
                    if 'processed_frame' in result:
                        processed = result['processed_frame']
                        # Ensure frame is correct size
                        if processed.shape[:2] != (height, width):
                            processed = cv2.resize(processed, (width, height))
                        self.video_writer.write(processed)
                        self.frames_processed += 1
                
                frame_number += 1
            
            cap.release()
            if self.video_writer:
                self.video_writer.release()
            
            # Get trajectory data
            traj_df = self.tracker.get_trajectory_dataframe()
            metrics = self.tracker.get_metrics()
            
            return {
                'success': True,
                'output_video': output_path,
                'frames_processed': self.frames_processed,
                'total_frames': total_frames,
                'fps': fps,
                'metrics': metrics,
                'trajectory_rows': len(traj_df) if traj_df is not None else 0
            }
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            if self.video_writer:
                self.video_writer.release()
            return {'error': str(e)}
    
    def get_trajectories_csv(self) -> Optional[str]:
        """
        Get trajectory data as CSV string
        
        Returns:
            CSV string or None if no data
        """
        try:
            traj_df = self.tracker.get_trajectory_dataframe()
            if traj_df is None:
                return None
            return traj_df.to_csv(index=False)
        except Exception as e:
            logger.error(f"Error generating CSV: {e}")
            return None
