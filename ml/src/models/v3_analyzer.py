"""
V3 Analyzer - Visualization wrapper for pedestrian tracking
Integrates tracker_ped.py with enhanced visualization capabilities
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import logging
import sys

logger = logging.getLogger(__name__)

# Add v3Updates to path
v3_path = Path(__file__).parent.parent / "v3Updates"
if str(v3_path) not in sys.path:
    sys.path.insert(0, str(v3_path))

try:
    from tracker_ped import CrowdDensityEstimation
except ImportError as e:
    logger.warning(f"Could not import tracker_ped: {e}")
    CrowdDensityEstimation = None


class PedestrianVisualizer:
    """
    Visualization engine for pedestrian tracking
    Draws trajectories, bounding boxes, track IDs, and count badges
    """
    
    def __init__(
        self,
        trajectory_max_points: int = 30,
        trajectory_max_distance_cm: float = 2.0,
        font_scale: float = 0.6,
        bbox_thickness: int = 2,
        trajectory_thickness: int = 2,
        id_text_thickness: int = 2,
    ):
        """
        Initialize visualizer
        
        Args:
            trajectory_max_points: Maximum number of trajectory points to show
            trajectory_max_distance_cm: Max distance in cm (for real-world scaling)
            font_scale: OpenCV font scale
            bbox_thickness: Bounding box line thickness
            trajectory_thickness: Trajectory line thickness
            id_text_thickness: ID text thickness
        """
        self.trajectory_max_points = trajectory_max_points
        self.trajectory_max_distance_cm = trajectory_max_distance_cm
        self.font_scale = font_scale
        self.bbox_thickness = bbox_thickness
        self.trajectory_thickness = trajectory_thickness
        self.id_text_thickness = id_text_thickness
        
        self.track_colors = {}
        self.frame_width = None
        self.frame_height = None
    
    def get_color(self, track_id: int) -> Tuple[int, int, int]:
        """Get consistent color for track ID"""
        if track_id not in self.track_colors:
            # Generate deterministic color based on track_id
            np.random.seed(track_id)
            self.track_colors[track_id] = tuple(
                int(np.random.randint(50, 255)) for _ in range(3)
            )
        return self.track_colors[track_id]
    
    def draw_bounding_boxes(
        self,
        frame: np.ndarray,
        results: Any,
    ) -> np.ndarray:
        """
        Draw bounding boxes with track IDs
        
        Args:
            frame: Video frame
            results: YOLO detection results
            
        Returns:
            Annotated frame
        """
        if results[0].boxes.id is None:
            return frame
        
        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy().astype(int)
        
        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = map(int, box)
            color = self.get_color(track_id)
            
            # Draw bounding box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                self.bbox_thickness
            )
            
            # Draw track ID with background
            id_text = f"ID:{track_id}"
            text_size = cv2.getTextSize(
                id_text,
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                self.id_text_thickness
            )[0]
            
            # Background rectangle for ID text
            cv2.rectangle(
                frame,
                (x1, y1 - text_size[1] - 5),
                (x1 + text_size[0] + 5, y1),
                color,
                -1
            )
            
            # ID text
            cv2.putText(
                frame,
                id_text,
                (x1 + 2, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                (255, 255, 255),
                self.id_text_thickness
            )
        
        return frame
    
    def draw_trajectories(
        self,
        frame: np.ndarray,
        track_history: Dict[int, List[Tuple[float, float]]],
        homography_matrix: Optional[np.ndarray] = None,
        max_points: Optional[int] = None,
    ) -> np.ndarray:
        """
        Draw trajectory lines for each track
        
        Args:
            frame: Video frame
            track_history: Dictionary mapping track_id to list of (x, y) points
            homography_matrix: Optional homography for world-to-image transform
            max_points: Override max points for this frame
            
        Returns:
            Annotated frame
        """
        if not track_history:
            return frame
        
        max_pts = max_points if max_points is not None else self.trajectory_max_points
        
        for track_id, points in track_history.items():
            if not points or len(points) < 2:
                continue
            
            color = self.get_color(track_id)
            
            # Use last N points
            trajectory_points = points[-max_pts:]
            
            # Draw trajectory line
            for i in range(1, len(trajectory_points)):
                pt1 = trajectory_points[i - 1]
                pt2 = trajectory_points[i]
                
                if pt1 is None or pt2 is None:
                    continue
                
                # Transform if homography provided
                if homography_matrix is not None:
                    try:
                        H_inv = np.linalg.inv(homography_matrix)
                        pt1 = self._world_to_image(pt1, H_inv)
                        pt2 = self._world_to_image(pt2, H_inv)
                    except Exception as e:
                        logger.debug(f"Homography transform error: {e}")
                        continue
                
                pt1 = tuple(map(int, pt1))
                pt2 = tuple(map(int, pt2))
                
                # Fade effect: older points are faded
                alpha = i / len(trajectory_points)
                faded_color = tuple(int(c * alpha) for c in color)
                
                cv2.line(
                    frame,
                    pt1,
                    pt2,
                    faded_color,
                    self.trajectory_thickness
                )
            
            # Draw trajectory start point as circle
            if trajectory_points:
                start_pt = trajectory_points[0]
                if start_pt is not None:
                    if homography_matrix is not None:
                        try:
                            H_inv = np.linalg.inv(homography_matrix)
                            start_pt = self._world_to_image(start_pt, H_inv)
                        except:
                            pass
                    
                    start_pt = tuple(map(int, start_pt))
                    cv2.circle(frame, start_pt, 4, color, -1)
        
        return frame
    
    def draw_count_badge(
        self,
        frame: np.ndarray,
        unique_count: int,
        current_count: int,
        position: str = "bottom-right",
    ) -> np.ndarray:
        """
        Draw count badge (unique and current counts)
        
        Args:
            frame: Video frame
            unique_count: Total unique pedestrians tracked
            current_count: Current pedestrians in frame
            position: 'bottom-right', 'bottom-left', 'top-right', 'top-left'
            
        Returns:
            Annotated frame with badge
        """
        if self.frame_height is None or self.frame_width is None:
            self.frame_height, self.frame_width = frame.shape[:2]
        
        badge_text = f"Unique: {unique_count} | Current: {current_count}"
        text_size = cv2.getTextSize(
            badge_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            self.font_scale + 0.2,
            self.id_text_thickness
        )[0]
        
        padding = 10
        badge_width = text_size[0] + 2 * padding
        badge_height = text_size[1] + 2 * padding
        
        # Determine position
        if position == "bottom-right":
            x = self.frame_width - badge_width - padding
            y = self.frame_height - padding
        elif position == "bottom-left":
            x = padding
            y = self.frame_height - padding
        elif position == "top-right":
            x = self.frame_width - badge_width - padding
            y = badge_height + padding
        else:  # top-left
            x = padding
            y = badge_height + padding
        
        # Draw background
        cv2.rectangle(
            frame,
            (x, y - badge_height),
            (x + badge_width, y),
            (0, 0, 0),
            -1
        )
        
        # Draw border
        cv2.rectangle(
            frame,
            (x, y - badge_height),
            (x + badge_width, y),
            (0, 255, 0),
            2
        )
        
        # Draw text
        cv2.putText(
            frame,
            badge_text,
            (x + padding, y - padding),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.font_scale + 0.2,
            (0, 255, 0),
            self.id_text_thickness
        )
        
        return frame
    
    @staticmethod
    def _world_to_image(point: Tuple[float, float], H_inv: np.ndarray) -> Tuple[float, float]:
        """Convert world coordinates to image coordinates"""
        point_homo = np.array([point[0], point[1], 1.0]).reshape(3, 1)
        transformed = H_inv @ point_homo
        transformed = transformed / transformed[2]
        return (float(transformed[0][0]), float(transformed[1][0]))
    
    def annotate_frame(
        self,
        frame: np.ndarray,
        results: Any,
        track_history: Dict[int, List[Tuple[float, float]]],
        unique_count: int,
        current_count: int,
        homography_matrix: Optional[np.ndarray] = None,
        max_trajectory_points: Optional[int] = None,
        badge_position: str = "bottom-right",
    ) -> np.ndarray:
        """
        Annotate frame with all visualizations
        
        Args:
            frame: Video frame
            results: YOLO detection results
            track_history: Dictionary of trajectories
            unique_count: Total unique pedestrians
            current_count: Current pedestrians in frame
            homography_matrix: Optional homography matrix
            max_trajectory_points: Override max trajectory points
            badge_position: Badge position
            
        Returns:
            Fully annotated frame
        """
        self.frame_height, self.frame_width = frame.shape[:2]
        
        # Draw in order: trajectories, bboxes, count badge
        frame = self.draw_trajectories(
            frame,
            track_history,
            homography_matrix,
            max_trajectory_points
        )
        frame = self.draw_bounding_boxes(frame, results)
        frame = self.draw_count_badge(
            frame,
            unique_count,
            current_count,
            badge_position
        )
        
        return frame


class V3Analyzer:
    """
    High-level analyzer combining tracking and visualization
    """
    
    def __init__(
        self,
        model_path: str = 'yolo11n.pt',
        conf_threshold: float = 0.15,
        iou_threshold: float = 0.45,
        enable_visualization: bool = True,
        **visualizer_kwargs
    ):
        """
        Initialize analyzer
        
        Args:
            model_path: YOLO model path
            conf_threshold: Confidence threshold
            iou_threshold: IOU threshold
            enable_visualization: Enable visualization
            **visualizer_kwargs: Kwargs for PedestrianVisualizer
        """
        if CrowdDensityEstimation is None:
            raise ImportError("tracker_ped module not available")
        
        self.tracker = CrowdDensityEstimation(
            model_path=model_path,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold
        )
        
        self.visualizer = PedestrianVisualizer(**visualizer_kwargs) if enable_visualization else None
    
    def process_frame(
        self,
        frame: np.ndarray,
        frame_number: int = 0,
        max_trajectory_points: Optional[int] = None,
        annotate: bool = True,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process frame: detect, track, and optionally annotate
        
        Args:
            frame: Input frame
            frame_number: Frame number
            max_trajectory_points: Override max trajectory points
            annotate: Whether to annotate frame
            
        Returns:
            Tuple of (annotated_frame, metadata)
        """
        results, resized_frame = self.tracker.extract_tracks(frame)
        
        current_count = len(results[0].boxes.id) if results[0].boxes.id is not None else 0
        
        # Update trajectories
        self.tracker.update_trajectories(results, frame_number)
        
        metadata = {
            'frame_number': frame_number,
            'current_count': current_count,
            'unique_count': len(self.tracker.unique_persons),
            'track_count': len(self.tracker.track_history)
        }
        
        # Annotate if requested and visualizer available
        if annotate and self.visualizer:
            annotated_frame = self.visualizer.annotate_frame(
                resized_frame.copy(),
                results,
                self.tracker.track_history,
                metadata['unique_count'],
                metadata['current_count'],
                self.tracker.homography_matrix,
                max_trajectory_points
            )
            return annotated_frame, metadata
        
        return resized_frame, metadata
    
    def set_homography(self, points_image: List, points_world: List) -> None:
        """Set homography matrix for world coordinate transformation"""
        self.tracker.set_homography_matrix(points_image, points_world)
    
    def get_track_history(self) -> Dict[int, List[Tuple[float, float]]]:
        """Get current track history"""
        return dict(self.tracker.track_history)
    
    def save_trajectories(self, output_path: str) -> None:
        """Save trajectories to CSV"""
        self.tracker.save_trajectories(output_path)
