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
        device: str = None,  # None = auto-detect via DeviceManager
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
            device: 'cuda' or 'cpu' (None = auto-detect via DeviceManager)
            conf_threshold: Confidence threshold (YOLO only)
            iou_threshold: IOU threshold (YOLO only)
            enable_tracking: Enable Kalman filter tracking
            **kwargs: Additional model-specific parameters
        """
        self.model_type = model_type.lower()
        # Use DeviceManager for intelligent device selection
        if device is None:
            try:
                if get_device_manager is not None:
                    device = get_device_manager().current_device
                    logger.info(f"🖥️ UnifiedCounter using DeviceManager: {device}")
                else:
                    device = 'cuda' if torch.cuda.is_available() else 'cpu'
                    logger.info(f"🖥️ UnifiedCounter using torch check: {device}")
            except Exception as e:
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                logger.warning(f"⚠️ DeviceManager error, falling back: {e}, using {device}")
        self.device = device
        logger.info(f"✅ UnifiedCounter initialized with device: {self.device}")
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
            # Optimized parameters for stable tracking:
            # - Reduced max_distance for stricter matching (less ID switching)
            # - Increased max_age for longer persistence (less flickering)
            # - Increased min_hits for confirmation (less false tracks)
            self.tracker = KalmanTracker(max_distance=100.0, max_age=8, min_hits=3)
            logger.info("Tracking enabled with optimized parameters: max_distance=100, max_age=8, min_hits=3")
    
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
        # Base prediction (YOLO needs boxes for tracking)
        if self.model_type == 'yolo':
            request_boxes = bool(self.tracker is not None or return_details)
            result = self.model.predict(
                image,
                return_boxes=request_boxes
            )
        else:
            result = self.model.predict(image)
        
        # Add tracking if enabled
        if self.tracker is not None:
            boxes = result.get('boxes', [])
            tracker_boxes = self._prepare_tracker_boxes(boxes)
            
            if len(tracker_boxes) > 0:
                # Update tracker using normalized box format
                tracks = self.tracker.update(tracker_boxes)
                
                # Add tracking info to result
                result['tracks'] = [
                    {
                        'id': track.id,
                        'box': track.last_box,
                        'position': track.kf.x[:2].flatten().tolist(),
                        'state': int(track.state),  # Convert enum to int (0=NEW, 1=TRACKED, 2=LOST)
                        'speed': track.last_speed,  # Phase 2: Add speed
                        'avg_speed': track.get_average_speed(),  # Phase 2: Add average speed
                        'trajectory': [
                            [float(p[0]), float(p[1])] if isinstance(p, (tuple, list)) else [float(p), 0.0]
                            for p in self.tracker.track_history.get(track.id, [])[-30:]
                        ],  # Last 30 points as [x, y] arrays
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
            logger.info(f"🎨 Generating annotated image with {len(result.get('tracks', []))} tracks")
            result['annotated_image'] = self._draw_predictions(image, result)
            if result.get('annotated_image') is not None:
                logger.info(f"✅ Annotated image generated: shape={result['annotated_image'].shape}")
            else:
                logger.warning("⚠️ _draw_predictions returned None")
        
        return result
    
    def _get_color_for_id(self, track_id: int) -> Tuple[int, int, int]:
        """Generate unique BGR color for track ID using golden ratio for even distribution"""
        hue = (track_id * 137.508) % 360  # Golden angle
        # Convert HSV to BGR (OpenCV uses BGR)
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(hue / 360, 0.85, 0.9)
        return (int(b * 255), int(g * 255), int(r * 255))
    
    def _predict_future_positions(self, track_id: int, num_steps: int = 5) -> List[Tuple[int, int]]:
        """Predict future positions using Kalman filter velocity"""
        if track_id not in self.tracker.track_history:
            return []
        
        history = self.tracker.track_history[track_id]
        if len(history) < 2:
            return []
        
        # Calculate average velocity from recent points
        recent = history[-min(5, len(history)):]
        avg_vx, avg_vy = 0, 0
        for i in range(1, len(recent)):
            avg_vx += recent[i][0] - recent[i-1][0]
            avg_vy += recent[i][1] - recent[i-1][1]
        
        count = len(recent) - 1
        if count > 0:
            avg_vx /= count
            avg_vy /= count
        
        # Only predict if moving
        speed = np.sqrt(avg_vx**2 + avg_vy**2)
        if speed < 1.0:
            return []
        
        # Project forward
        last_pos = history[-1]
        predictions = []
        for i in range(1, num_steps + 1):
            pred_x = int(last_pos[0] + avg_vx * i * 1.5)  # Scale factor for visibility
            pred_y = int(last_pos[1] + avg_vy * i * 1.5)
            predictions.append((pred_x, pred_y))
        
        return predictions
    
    def _draw_predictions(self, image: np.ndarray, result: Dict) -> np.ndarray:
        """Draw enhanced predictions on image with bounding boxes, trajectories, and predictions"""
        annotated = image.copy()
        h, w = annotated.shape[:2]
        
        # Visualization toggles
        draw_bounding_boxes = False  # Set to True to enable bounding boxes
        draw_trajectories = True
        draw_predictions = True
        
        if self.model_type == 'yolo':
            if self.tracker is not None and 'tracks' in result:
                # Draw with enhanced styling
                for track_info in result['tracks']:
                    box = track_info['box']
                    track_id = track_info['id']
                    speed = track_info.get('speed', 0)
                    
                    # Get unique color for this track
                    color = self._get_color_for_id(track_id)
                    
                    x1, y1, x2, y2 = map(int, box[:4])
                    box_w, box_h = x2 - x1, y2 - y1
                    
                    # === Draw Bounding Box with Corner Accents ===
                    if draw_bounding_boxes:
                        # Main box (semi-transparent effect via thinner line)
                        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                        
                        # Corner accents
                        corner_len = min(20, box_w // 4, box_h // 4)
                        # Top-left
                        cv2.line(annotated, (x1, y1), (x1 + corner_len, y1), color, 3)
                        cv2.line(annotated, (x1, y1), (x1, y1 + corner_len), color, 3)
                        # Top-right
                        cv2.line(annotated, (x2, y1), (x2 - corner_len, y1), color, 3)
                        cv2.line(annotated, (x2, y1), (x2, y1 + corner_len), color, 3)
                        # Bottom-left
                        cv2.line(annotated, (x1, y2), (x1 + corner_len, y2), color, 3)
                        cv2.line(annotated, (x1, y2), (x1, y2 - corner_len), color, 3)
                        # Bottom-right
                        cv2.line(annotated, (x2, y2), (x2 - corner_len, y2), color, 3)
                        cv2.line(annotated, (x2, y2), (x2, y2 - corner_len), color, 3)
                        
                        # === Draw ID Label with Background ===
                        label = f"#{track_id}"
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.6
                        thickness = 2
                        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                        
                        # Label background
                        cv2.rectangle(annotated, (x1, y1 - text_h - 8), (x1 + text_w + 8, y1), color, -1)
                        cv2.putText(annotated, label, (x1 + 4, y1 - 4), font, font_scale, (255, 255, 255), thickness)
                        
                        # === Draw Speed Badge ===
                        if speed > 0.1:
                            speed_text = f"{speed:.1f} px/s"
                            (sw, sh), _ = cv2.getTextSize(speed_text, font, 0.5, 1)
                            cv2.rectangle(annotated, (x2 - sw - 8, y1 - sh - 8), (x2, y1), (40, 40, 40), -1)
                            cv2.putText(annotated, speed_text, (x2 - sw - 4, y1 - 4), font, 0.5, color, 1)
                    
                    # === Draw Trajectory Path (Gradient Opacity) ===
                    if draw_trajectories and track_id in self.tracker.track_history:
                        points = self.tracker.track_history[track_id]
                        num_points = len(points)
                        
                        # Only draw trajectory if we have at least 3 points (for smoother paths)
                        if num_points >= 3:
                            # Apply smoothing to trajectory points
                            smoothed_points = []
                            for i in range(num_points):
                                # Simple moving average smoothing
                                start_idx = max(0, i - 1)
                                end_idx = min(num_points, i + 2)
                                window_points = points[start_idx:end_idx]
                                
                                # Average the positions
                                avg_x = sum(p[0] for p in window_points) / len(window_points)
                                avg_y = sum(p[1] for p in window_points) / len(window_points)
                                smoothed_points.append([avg_x, avg_y])
                            
                            # Draw smoothed trajectory
                            for i in range(1, len(smoothed_points)):
                                # Gradient: older points are more transparent (thinner)
                                alpha = i / len(smoothed_points)
                                line_thickness = max(1, int(alpha * 2))  # Thinner lines for cleaner look
                                
                                pt1 = tuple(map(int, smoothed_points[i-1]))
                                pt2 = tuple(map(int, smoothed_points[i]))
                                cv2.line(annotated, pt1, pt2, color, line_thickness)
                            
                            # Draw start marker (small circle) - only if trajectory is established
                            start_pt = tuple(map(int, smoothed_points[0]))
                            cv2.circle(annotated, start_pt, 4, color, 1)  # Smaller marker
                            
                            # Draw current position marker (filled circle)
                            end_pt = tuple(map(int, smoothed_points[-1]))
                            cv2.circle(annotated, end_pt, 6, color, -1)  # Smaller end marker
                            cv2.circle(annotated, end_pt, 6, (255, 255, 255), 1)  # Thinner border
                        elif num_points >= 2:
                            # For short trajectories, draw without smoothing but with minimal styling
                            for i in range(1, num_points):
                                pt1 = tuple(map(int, points[i-1][:2]))
                                pt2 = tuple(map(int, points[i][:2]))
                                cv2.line(annotated, pt1, pt2, color, 1)  # Thin line
                        elif num_points == 1:
                            # Single point - just draw a small indicator (no big circle)
                            pt = tuple(map(int, points[0][:2]))
                            cv2.circle(annotated, pt, 4, color, -1)
                    
                    # === Draw Predicted Path (Dashed) - only for established tracks ===
                    if draw_predictions and track_id in self.tracker.track_history:
                        track_history = self.tracker.track_history[track_id]
                        # Only draw predictions if track has at least 3 points (enough to establish direction)
                        if len(track_history) >= 3:
                            predictions = self._predict_future_positions(track_id, num_steps=5)
                            if predictions:
                                # Start from last known position
                                last_pos = tuple(map(int, track_history[-1][:2]))
                                
                                # Draw dashed prediction line
                                all_pred_points = [last_pos] + predictions
                                for i in range(1, len(all_pred_points)):
                                    pt1 = all_pred_points[i-1]
                                    pt2 = all_pred_points[i]
                                    
                                    # Dashed line effect
                                    dist = np.sqrt((pt2[0]-pt1[0])**2 + (pt2[1]-pt1[1])**2)
                                    if dist > 0:
                                        num_dashes = max(2, int(dist / 8))
                                        for d in range(0, num_dashes, 2):
                                            t1 = d / num_dashes
                                            t2 = min((d + 1) / num_dashes, 1.0)
                                            dash_pt1 = (int(pt1[0] + t1 * (pt2[0] - pt1[0])), 
                                                       int(pt1[1] + t1 * (pt2[1] - pt1[1])))
                                            dash_pt2 = (int(pt1[0] + t2 * (pt2[0] - pt1[0])), 
                                                       int(pt1[1] + t2 * (pt2[1] - pt1[1])))
                                            # Lighter color for predictions
                                            pred_color = tuple(min(255, c + 60) for c in color)
                                            cv2.line(annotated, dash_pt1, dash_pt2, pred_color, 2)
                                
                                # Arrow at end of prediction
                                if len(predictions) >= 2:
                                    end_pt = predictions[-1]
                                    prev_pt = predictions[-2]
                                angle = np.arctan2(end_pt[1] - prev_pt[1], end_pt[0] - prev_pt[0])
                                arrow_len = 12
                                
                                arr_pt1 = (int(end_pt[0] - arrow_len * np.cos(angle - np.pi/6)),
                                          int(end_pt[1] - arrow_len * np.sin(angle - np.pi/6)))
                                arr_pt2 = (int(end_pt[0] - arrow_len * np.cos(angle + np.pi/6)),
                                          int(end_pt[1] - arrow_len * np.sin(angle + np.pi/6)))
                                
                                pred_color = tuple(min(255, c + 60) for c in color)
                                cv2.line(annotated, end_pt, arr_pt1, pred_color, 2)
                                cv2.line(annotated, end_pt, arr_pt2, pred_color, 2)
            
            else:
                # Draw simple boxes without tracking
                boxes = result.get('boxes', [])
                for box in boxes:
                    if isinstance(box, dict) and 'bbox' in box:
                        coords = box['bbox']
                    else:
                        coords = box
                    x1, y1, x2, y2 = map(int, coords[:4])
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # === Draw Stats Overlay ===
            # Semi-transparent background for stats
            overlay = annotated.copy()
            cv2.rectangle(overlay, (5, 5), (200, 90), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, annotated, 0.4, 0, annotated)
            
            # Count
            count_text = f"Count: {result['count']}"
            cv2.putText(annotated, count_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Unique count
            if 'unique_count' in result:
                unique_text = f"Tracked: {result['unique_count']}"
                cv2.putText(annotated, unique_text, (15, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Average speed
            if 'speed_stats' in result and result['speed_stats'].get('average', 0) > 0:
                speed_text = f"Avg Speed: {result['speed_stats']['average']:.1f} px/s"
                cv2.putText(annotated, speed_text, (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 100), 1)
        
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

    def _prepare_tracker_boxes(self, boxes: List) -> List[List[float]]:
        """Normalize box outputs into [x1, y1, x2, y2] format for the tracker"""
        formatted_boxes = []
        for box in boxes or []:
            coords = None
            if isinstance(box, dict):
                if 'bbox' in box and len(box['bbox']) >= 4:
                    coords = box['bbox'][:4]
                elif all(k in box for k in ('x1', 'y1', 'x2', 'y2')):
                    coords = [box['x1'], box['y1'], box['x2'], box['y2']]
            elif isinstance(box, (list, tuple, np.ndarray)) and len(box) >= 4:
                coords = box[:4]

            if coords is None:
                continue

            try:
                formatted_boxes.append([float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3])])
            except (TypeError, ValueError):
                continue
        return formatted_boxes
    
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
