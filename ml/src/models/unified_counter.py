"""
Unified Crowd Counter
Supports multiple models with optional tracking and advanced crowd analysis
"""
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class UnifiedCounter:
    """
    Unified interface for all counting models with optional tracking
    """
    
    def __init__(
        self,
        model_type: str = 'yolo',
        model_path: Optional[str] = None,
        device: str = 'cuda',
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        enable_tracking: bool = False,
        **kwargs
    ):
        """
        Initialize unified counter
        
        Args:
            model_type: 'yolo', 'csrnet', or 'mcnn'
            model_path: Path to model weights
            device: 'cuda' or 'cpu'
            conf_threshold: Confidence threshold (YOLO only)
            iou_threshold: IOU threshold (YOLO only)
            enable_tracking: Enable Kalman filter tracking
            **kwargs: Additional model-specific parameters
        """
        self.model_type = model_type.lower()
        self.device = device
        self.enable_tracking = enable_tracking
        self.model = None
        self.tracker = None
        
        # Load appropriate model
        if self.model_type == 'yolo':
            from models.yolo.yolov8_counter import YOLOv8Counter
            
            if model_path is None:
                model_path = 'yolov8n.pt'
            
            self.model = YOLOv8Counter(
                model_path=model_path,
                device=device,
                conf_threshold=conf_threshold,
                iou_threshold=iou_threshold
            )
            logger.info(f"Loaded YOLO model: {model_path}")
            
        elif self.model_type == 'csrnet':
            from models.csrnet.model import CSRNet
            
            if model_path is None:
                model_path = 'ml/checkpoints/csrnet.pth'
            
            self.model = CSRNet(
                checkpoint=model_path,
                device=device
            )
            logger.info(f"Loaded CSRNet model: {model_path}")
            
        elif self.model_type == 'mcnn':
            from models.mcnn.model import MCNN
            
            if model_path is None:
                model_path = 'ml/checkpoints/mcnn.pth'
            
            self.model = MCNN(
                checkpoint=model_path,
                device=device
            )
            logger.info(f"Loaded MCNN model: {model_path}")
            
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Initialize tracker if enabled (only for YOLO)
        if self.enable_tracking and self.model_type == 'yolo':
            from models.tracking import KalmanTracker
            self.tracker = KalmanTracker()
            logger.info("Tracking enabled")
    
    def predict(
        self,
        image: np.ndarray,
        return_details: bool = False,
        return_visualization: bool = False
    ) -> Dict[str, Any]:
        """
        Unified prediction interface
        
        Args:
            image: Input image (BGR or RGB)
            return_details: Return detailed information
            return_visualization: Return annotated image
            
        Returns:
            Dictionary with prediction results
        """
        # Base prediction
        result = self.model.predict(image)
        
        # Add tracking if enabled
        if self.tracker is not None:
            boxes = result.get('boxes', [])
            
            if len(boxes) > 0:
                # Update tracker
                tracks = self.tracker.update(boxes)
                
                # Add tracking info to result
                result['tracks'] = [
                    {
                        'id': track.id,
                        'box': track.last_box,
                        'position': track.kf.x[:2].flatten().tolist(),
                        'state': int(track.state),  # Convert enum to int (0=NEW, 1=TRACKED, 2=LOST)
                        'speed': track.last_speed,  # Phase 2: Add speed
                        'avg_speed': track.get_average_speed(),  # Phase 2: Add average speed
                        'trajectory': self.tracker.track_history.get(track.id, [])[-30:],  # Last 30 points
                        'frames_tracked': track.hits  # Number of frames this track has been detected
                    }
                    for track in tracks
                ]
                result['unique_count'] = len(set(t.id for t in tracks))
                result['tracking_enabled'] = True
                
                # Phase 2: Calculate speed statistics
                speeds = [t.last_speed for t in tracks if t.last_speed > 0]
                if speeds:
                    result['speed_stats'] = {
                        'average': float(np.mean(speeds)),
                        'max': float(np.max(speeds)),
                        'min': float(np.min(speeds)),
                        'std': float(np.std(speeds))
                    }
                else:
                    result['speed_stats'] = {'average': 0.0, 'max': 0.0, 'min': 0.0, 'std': 0.0}
            else:
                result['tracks'] = []
                result['unique_count'] = 0
                result['tracking_enabled'] = True
                result['speed_stats'] = {'average': 0.0, 'max': 0.0, 'min': 0.0, 'std': 0.0}
        
        # Generate visualization if requested
        if return_visualization:
            result['annotated_image'] = self._draw_predictions(image, result)
        
        return result
    
    def _draw_predictions(self, image: np.ndarray, result: Dict) -> np.ndarray:
        """Draw predictions on image"""
        annotated = image.copy()
        
        if self.model_type == 'yolo':
            # Draw bounding boxes
            boxes = result.get('boxes', [])
            
            if self.tracker is not None and 'tracks' in result:
                # Draw with track IDs and speed-based colors (Phase 2)
                for track_info in result['tracks']:
                    box = track_info['box']
                    track_id = track_info['id']
                    
                    # Phase 2: Use speed-based coloring
                    track_obj = next((t for t in self.tracker.tracks if t.id == track_id), None)
                    if track_obj and track_obj.last_speed > 0:
                        # Color by speed (blue=slow, red=fast)
                        color = self.tracker.get_speed_color(track_obj.last_speed, max_speed=100.0)
                    else:
                        # Fallback to consistent color
                        color = self.tracker.get_color(track_id)
                    
                    # Draw box
                    x1, y1, x2, y2 = map(int, box[:4])
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw ID and speed
                    label = f"ID:{track_id}"
                    if track_obj:
                        label += f" {track_obj.last_speed:.1f}px/s"
                    
                    cv2.putText(
                        annotated, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                    )
                    
                    # Draw trajectory
                    if track_id in self.tracker.track_history:
                        points = self.tracker.track_history[track_id]
                        for i in range(1, len(points)):
                            pt1 = tuple(map(int, points[i-1]))
                            pt2 = tuple(map(int, points[i]))
                            cv2.line(annotated, pt1, pt2, color, 1)
            else:
                # Draw simple boxes without tracking
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box[:4])
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw counts
            count_text = f"Count: {result['count']}"
            cv2.putText(
                annotated, count_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )
            
            if 'unique_count' in result:
                unique_text = f"Unique: {result['unique_count']}"
                cv2.putText(
                    annotated, unique_text, (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
                )
        
        elif self.model_type in ['csrnet', 'mcnn']:
            # Draw density map overlay
            if 'density_map' in result and result['density_map'] is not None:
                density_map = result['density_map']
                
                # Resize to match image
                h, w = image.shape[:2]
                density_resized = cv2.resize(density_map, (w, h))
                
                # Normalize and colorize
                density_norm = cv2.normalize(
                    density_resized, None, 0, 255, cv2.NORM_MINMAX
                ).astype(np.uint8)
                density_colored = cv2.applyColorMap(density_norm, cv2.COLORMAP_JET)
                
                # Blend with original
                annotated = cv2.addWeighted(annotated, 0.6, density_colored, 0.4, 0)
            
            # Draw count
            count_text = f"Count: {result['count']:.1f}"
            cv2.putText(
                annotated, count_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )
        
        return annotated
    
    def process_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        max_frames: Optional[int] = None,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Process entire video
        
        Args:
            video_path: Path to input video
            output_path: Path to save annotated video (optional)
            max_frames: Maximum frames to process
            show_progress: Show progress bar
            
        Returns:
            Dictionary with video-level statistics
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Video writer
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Process frames
        frame_counts = []
        unique_counts = []
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if max_frames and frame_idx >= max_frames:
                break
            
            # Predict
            result = self.predict(frame, return_visualization=(writer is not None))
            
            frame_counts.append(result['count'])
            if 'unique_count' in result:
                unique_counts.append(result['unique_count'])
            
            # Write frame
            if writer and 'annotated_image' in result:
                writer.write(result['annotated_image'])
            
            # Progress
            if show_progress and frame_idx % 30 == 0:
                print(f"Processed {frame_idx}/{total_frames} frames...")
            
            frame_idx += 1
        
        cap.release()
        if writer:
            writer.release()
        
        # Statistics
        stats = {
            'total_frames': frame_idx,
            'avg_count': np.mean(frame_counts) if frame_counts else 0,
            'max_count': np.max(frame_counts) if frame_counts else 0,
            'min_count': np.min(frame_counts) if frame_counts else 0,
        }
        
        if unique_counts:
            stats['max_unique'] = np.max(unique_counts)
        
        return stats
    
    def reset_tracker(self):
        """Reset tracker state"""
        if self.tracker:
            self.tracker.reset()
    
    def export_trajectory_data(self, frame_rate: int = 30):
        """
        Export trajectory data for PedPy analysis
        
        Args:
            frame_rate: Video frame rate (fps)
            
        Returns:
            TrajectoryData object or None if no tracking data
        """
        if not self.tracker or not self.tracker.track_history:
            return None
        
        try:
            from pedpy import TrajectoryData
            
            # Convert track history to DataFrame format for PedPy
            rows = []
            for track_id, positions in self.tracker.track_history.items():
                for frame_idx, (x, y) in enumerate(positions):
                    rows.append({
                        'id': int(track_id),
                        'frame': int(frame_idx),
                        'x': float(x),
                        'y': float(y)
                    })
            
            if not rows:
                return None
            
            df = pd.DataFrame(rows)
            traj_data = TrajectoryData(data=df, frame_rate=frame_rate)
            
            return traj_data
        except ImportError:
            logger.warning("PedPy not installed. Cannot export trajectory data.")
            return None
        except Exception as e:
            logger.error(f"Error exporting trajectory data: {e}")
            return None
    
    def calculate_density_metrics(
        self, 
        trajectory_data,
        walkable_area,
        measurement_area
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate different density metrics using PedPy
        
        Args:
            trajectory_data: TrajectoryData object
            walkable_area: WalkableArea polygon
            measurement_area: MeasurementArea polygon
            
        Returns:
            Dictionary with classic_density, voronoi_density, voronoi_density_cutoff
        """
        try:
            from pedpy import (
                compute_classic_density,
                compute_individual_voronoi_polygons,
                compute_voronoi_density,
                Cutoff
            )
            
            # Classic density
            classic_density = compute_classic_density(
                traj_data=trajectory_data,
                measurement_area=measurement_area
            )
            
            # Voronoi density
            individual = compute_individual_voronoi_polygons(
                traj_data=trajectory_data,
                walkable_area=walkable_area
            )
            
            density_voronoi, intersecting = compute_voronoi_density(
                individual_voronoi_data=individual,
                measurement_area=measurement_area
            )
            
            # Voronoi with cutoff
            individual_cutoff = compute_individual_voronoi_polygons(
                traj_data=trajectory_data,
                walkable_area=walkable_area,
                cut_off=Cutoff(radius=12.0, quad_segments=1)
            )
            
            density_voronoi_cutoff, _ = compute_voronoi_density(
                individual_voronoi_data=individual_cutoff,
                measurement_area=measurement_area
            )
            
            return {
                'classic_density': classic_density,
                'voronoi_density': density_voronoi,
                'voronoi_density_cutoff': density_voronoi_cutoff,
                'individual': individual,
                'intersecting': intersecting
            }
        except ImportError:
            logger.warning("PedPy not installed. Cannot calculate density metrics.")
            return None
        except Exception as e:
            logger.error(f"Error calculating density metrics: {e}")
            return None
    
    def calculate_speed_metrics(
        self,
        trajectory_data,
        measurement_area,
        intersecting,
        frame_step: int = 25,
        movement_direction: Optional[np.ndarray] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate different speed metrics using PedPy
        
        Args:
            trajectory_data: TrajectoryData object
            measurement_area: MeasurementArea polygon
            intersecting: Voronoi intersection data
            frame_step: Frame step for speed calculation
            movement_direction: Optional movement direction vector
            
        Returns:
            Dictionary with mean_speed, voronoi_speed, directional speeds
        """
        try:
            from pedpy import (
                compute_individual_speed,
                compute_mean_speed_per_frame,
                compute_voronoi_speed,
                SpeedCalculation
            )
            
            # Individual speed (single-sided border)
            individual_speed = compute_individual_speed(
                traj_data=trajectory_data,
                frame_step=frame_step,
                compute_velocity=True,
                speed_calculation=SpeedCalculation.BORDER_SINGLE_SIDED
            )
            
            # Mean speed per frame
            mean_speed = compute_mean_speed_per_frame(
                traj_data=trajectory_data,
                measurement_area=measurement_area,
                individual_speed=individual_speed
            )
            
            # Voronoi-based speed
            voronoi_speed = compute_voronoi_speed(
                traj_data=trajectory_data,
                individual_voronoi_intersection=intersecting,
                individual_speed=individual_speed,
                measurement_area=measurement_area
            )
            
            result = {
                'mean_speed': mean_speed,
                'voronoi_speed': voronoi_speed
            }
            
            # Direction-based speed (if direction provided)
            if movement_direction is not None:
                individual_speed_direction = compute_individual_speed(
                    traj_data=trajectory_data,
                    frame_step=5,
                    movement_direction=movement_direction,
                    compute_velocity=True,
                    speed_calculation=SpeedCalculation.BORDER_SINGLE_SIDED
                )
                
                mean_speed_direction = compute_mean_speed_per_frame(
                    traj_data=trajectory_data,
                    measurement_area=measurement_area,
                    individual_speed=individual_speed_direction
                )
                
                voronoi_speed_direction = compute_voronoi_speed(
                    traj_data=trajectory_data,
                    individual_voronoi_intersection=intersecting,
                    individual_speed=individual_speed_direction,
                    measurement_area=measurement_area
                )
                
                result['mean_speed_direction'] = mean_speed_direction
                result['voronoi_speed_direction'] = voronoi_speed_direction
            
            return result
        except ImportError:
            logger.warning("PedPy not installed. Cannot calculate speed metrics.")
            return None
        except Exception as e:
            logger.error(f"Error calculating speed metrics: {e}")
            return None
    
    def get_advanced_metrics(
        self,
        frame_shape: Tuple[int, int],
        frame_rate: int = 30,
        frame_step: int = 25
    ) -> Optional[Dict[str, Any]]:
        """
        Get advanced crowd analysis metrics (density, speed, trajectories)
        
        Args:
            frame_shape: (height, width) of video frame
            frame_rate: Video frame rate
            frame_step: Frame step for speed calculation
            
        Returns:
            Dictionary with density and speed metrics, or None if not available
        """
        if not self.tracker or not self.tracker.track_history:
            return None
        
        try:
            from pedpy import WalkableArea, MeasurementArea
            
            # Export trajectory data
            traj_data = self.export_trajectory_data(frame_rate=frame_rate)
            if traj_data is None:
                return None
            
            height, width = frame_shape
            
            # Define walkable and measurement areas (full frame by default)
            walkable_polygon = np.array([
                [0, 0],
                [width, 0],
                [width, height],
                [0, height]
            ])
            walkable_area = WalkableArea(polygon=walkable_polygon)
            
            measurement_polygon = np.array([
                [0, 0],
                [width, 0],
                [width, height],
                [0, height]
            ])
            measurement_area = MeasurementArea(polygon=measurement_polygon)
            
            # Calculate density metrics
            density_metrics = self.calculate_density_metrics(
                traj_data,
                walkable_area,
                measurement_area
            )
            
            if density_metrics is None:
                return None
            
            # Calculate speed metrics
            speed_metrics = self.calculate_speed_metrics(
                traj_data,
                measurement_area,
                density_metrics['intersecting'],
                frame_step=frame_step
            )
            
            if speed_metrics is None:
                return None
            
            # Extract latest values
            result = {
                'density_metrics': {
                    'classic_density': float(density_metrics['classic_density'].iloc[-1]) if len(density_metrics['classic_density']) > 0 else 0.0,
                    'voronoi_density': float(density_metrics['voronoi_density'].iloc[-1]) if len(density_metrics['voronoi_density']) > 0 else 0.0,
                    'voronoi_density_cutoff': float(density_metrics['voronoi_density_cutoff'].iloc[-1]) if len(density_metrics['voronoi_density_cutoff']) > 0 else 0.0
                },
                'speed_metrics': {
                    'mean_speed': float(speed_metrics['mean_speed'].iloc[-1]) if len(speed_metrics['mean_speed']) > 0 else 0.0,
                    'voronoi_speed': float(speed_metrics['voronoi_speed'].iloc[-1]) if len(speed_metrics['voronoi_speed']) > 0 else 0.0,
                }
            }
            
            # Add directional speeds if available
            if 'mean_speed_direction' in speed_metrics:
                result['speed_metrics']['mean_speed_direction'] = float(speed_metrics['mean_speed_direction'].iloc[-1]) if len(speed_metrics['mean_speed_direction']) > 0 else 0.0
            if 'voronoi_speed_direction' in speed_metrics:
                result['speed_metrics']['voronoi_speed_direction'] = float(speed_metrics['voronoi_speed_direction'].iloc[-1]) if len(speed_metrics['voronoi_speed_direction']) > 0 else 0.0
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting advanced metrics: {e}")
            return None
