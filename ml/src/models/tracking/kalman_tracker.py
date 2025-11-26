"""
Kalman Filter Tracking Module
Extracted and adapted from v3Updates for production use
"""
import numpy as np
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter
from typing import List, Tuple, Optional
from collections import defaultdict
import random


class TrackState:
    """Track state enum"""
    NEW = 0
    TRACKED = 1
    LOST = 2


class Track:
    """Individual track with Kalman filter"""
    
    def __init__(self, box: List[float], track_id: int):
        """
        Initialize track
        
        Args:
            box: [x1, y1, x2, y2] bounding box
            track_id: Unique track ID
        """
        self.id = track_id
        self.state = TrackState.NEW
        self.age = 0
        self.hits = 0
        self.time_since_update = 0
        
        # Initialize Kalman filter (x, y, vx, vy)
        self.kf = KalmanFilter(dim_x=4, dim_z=2)
        x, y = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        self.kf.x = np.array([[x], [y], [0], [0]])
        
        # State transition matrix
        self.kf.F = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Measurement matrix
        self.kf.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        
        # Covariances - Increased process noise for better tracking, reduced measurement noise
        self.kf.P *= 10  # Initial state covariance
        self.kf.R *= 0.5  # Measurement noise (reduced from 1.0 for less jitter)
        self.kf.Q *= 0.05  # Process noise (reduced from 0.1 for smoother tracking)
        
        self.last_box = box
        
        # Speed tracking (for Phase 2 implementation)
        self.speeds = []  # Frame-by-frame speeds
        self.prev_position = np.array([x, y])
        self.max_speed_history = 15  # Keep last 15 speeds for averaging
        self.last_speed = 0.0  # Current frame speed
    
    def predict(self) -> np.ndarray:
        """Predict next position"""
        self.kf.predict()
        return self.kf.x[:2].flatten()
    
    def calculate_speed(self, current_position: np.ndarray, fps: float = 30.0) -> float:
        """
        Calculate speed between current and previous position
        
        Args:
            current_position: [x, y] center position
            fps: Frames per second for speed normalization
            
        Returns:
            Speed in pixels/second
        """
        # Euclidean distance
        distance = np.linalg.norm(current_position - self.prev_position)
        
        # Convert to pixels/second (assuming dt = 1/fps)
        speed = distance * fps
        
        # Add to history
        self.speeds.append(speed)
        if len(self.speeds) > self.max_speed_history:
            self.speeds.pop(0)
        
        self.prev_position = current_position.copy()
        return speed
    
    def get_average_speed(self) -> float:
        """Get smoothed average speed"""
        if not self.speeds:
            return 0.0
        return np.mean(self.speeds)
    
    def update(self, measurement: np.ndarray):
        """Update with new measurement"""
        self.kf.update(measurement)
        self.hits += 1
        self.time_since_update = 0
        
        # Transition to TRACKED after 2 hits (was 3)
        if self.state == TrackState.NEW and self.hits >= 2:
            self.state = TrackState.TRACKED
    
    def mark_missed(self):
        """Mark track as missed this frame"""
        self.time_since_update += 1
        
        # Transition to LOST after missing frames
        # NEW tracks are lost quickly (3 frames), TRACKED tracks can survive longer (5 frames)
        if self.state == TrackState.NEW and self.time_since_update > 3:
            self.state = TrackState.LOST
        elif self.state == TrackState.TRACKED and self.time_since_update > 5:
            self.state = TrackState.LOST


class KalmanTracker:
    """
    Kalman filter based tracker with Hungarian matching
    """
    
    def __init__(
        self,
        max_distance: float = 30.0,
        max_age: int = 10,
        min_hits: int = 3
    ):
        """
        Initialize tracker
        
        Args:
            max_distance: Maximum distance for matching
            max_age: Maximum frames to keep lost tracks
            min_hits: Minimum hits to confirm track
        """
        self.max_distance = max_distance
        self.max_age = max_age
        self.min_hits = min_hits
        
        self.tracks: List[Track] = []
        self.next_id = 0
        
        # Track history for visualization
        self.track_history = defaultdict(list)
        self.track_colors = {}
    
    def update(self, detections: List[List[float]]) -> List[Track]:
        """
        Update tracks with new detections
        
        Args:
            detections: List of [x1, y1, x2, y2] boxes
            
        Returns:
            List of active tracks
        """
        # Predict all tracks
        for track in self.tracks:
            track.predict()
        
        # Match detections to tracks
        if len(detections) > 0 and len(self.tracks) > 0:
            matched, unmatched_dets, unmatched_tracks = self._match_detections(detections)
            
            # Update matched tracks
            for det_idx, track_idx in matched:
                detection = detections[det_idx]
                center = np.array([
                    (detection[0] + detection[2]) / 2,
                    (detection[1] + detection[3]) / 2
                ])
                self.tracks[track_idx].update(center)
                self.tracks[track_idx].last_box = detection
                
                # Phase 2: Calculate speed for this track
                speed = self.tracks[track_idx].calculate_speed(center, fps=30.0)
                self.tracks[track_idx].last_speed = speed
            
            # Mark unmatched tracks as missed
            for track_idx in unmatched_tracks:
                self.tracks[track_idx].mark_missed()
            
            # Create new tracks for unmatched detections
            for det_idx in unmatched_dets:
                self._initiate_track(detections[det_idx])
        
        elif len(detections) > 0:
            # No existing tracks, create all
            for detection in detections:
                self._initiate_track(detection)
        
        else:
            # No detections, mark all as missed
            for track in self.tracks:
                track.mark_missed()
        
        # Remove lost tracks but keep reference for reporting
        lost_track_ids = [t.id for t in self.tracks if t.state == TrackState.LOST]
        self.tracks = [t for t in self.tracks if t.state != TrackState.LOST]
        
        # Clean up track history for lost tracks
        for track_id in lost_track_ids:
            if track_id in self.track_history:
                del self.track_history[track_id]
            if track_id in self.track_colors:
                del self.track_colors[track_id]
        
        # Update track history for all active tracks (NEW and TRACKED)
        for track in self.tracks:
            if track.state != TrackState.LOST:
                pos = track.kf.x[:2].flatten()
                # Store as list [x, y] for frontend compatibility
                self.track_history[track.id].append([float(pos[0]), float(pos[1])])
                
                # Limit history length
                if len(self.track_history[track.id]) > 50:
                    self.track_history[track.id].pop(0)
        
        # Return all active tracks (NEW + TRACKED) so UI can show warm-up state
        return [t for t in self.tracks if t.state != TrackState.LOST]
    
    def _match_detections(
        self,
        detections: List[List[float]]
    ) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
        """
        Match detections to tracks using Hungarian algorithm
        
        Returns:
            matched: List of (detection_idx, track_idx) pairs
            unmatched_detections: List of detection indices
            unmatched_tracks: List of track indices
        """
        # Compute cost matrix (Euclidean distance)
        det_centers = np.array([
            [(d[0] + d[2]) / 2, (d[1] + d[3]) / 2]
            for d in detections
        ])
        
        track_centers = np.array([
            t.kf.x[:2].flatten()
            for t in self.tracks
        ])
        
        # Distance matrix
        cost_matrix = np.linalg.norm(
            det_centers[:, np.newaxis] - track_centers,
            axis=2
        )
        
        # Hungarian matching
        if cost_matrix.size == 0:
            return [], list(range(len(detections))), list(range(len(self.tracks)))
        
        row_idx, col_idx = linear_sum_assignment(cost_matrix)
        
        # Filter by distance threshold
        matched = []
        unmatched_dets = list(range(len(detections)))
        unmatched_tracks = list(range(len(self.tracks)))
        
        for r, c in zip(row_idx, col_idx):
            if cost_matrix[r, c] < self.max_distance:
                matched.append((r, c))
                if r in unmatched_dets:
                    unmatched_dets.remove(r)
                if c in unmatched_tracks:
                    unmatched_tracks.remove(c)
            else:
                # Too far, don't match
                pass
        
        return matched, unmatched_dets, unmatched_tracks
    
    def _initiate_track(self, detection: List[float]):
        """Create new track from detection"""
        track = Track(detection, self.next_id)
        self.tracks.append(track)
        self.next_id += 1
    
    def get_tracked_tracks(self) -> List[Track]:
        """Get only confirmed tracked objects"""
        return [t for t in self.tracks if t.state == TrackState.TRACKED]
    
    def get_all_tracks(self) -> List[Track]:
        """Get all active tracks"""
        return self.tracks
    
    def get_color(self, track_id: int) -> Tuple[int, int, int]:
        """Get consistent color for track"""
        if track_id not in self.track_colors:
            self.track_colors[track_id] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
        return self.track_colors[track_id]
    
    def get_speed_color(self, speed: float, max_speed: float = 100.0) -> Tuple[int, int, int]:
        """
        Phase 2: Get color based on speed (blue=slow, red=fast)
        
        Args:
            speed: Current speed in pixels/second
            max_speed: Maximum speed for normalization
            
        Returns:
            (B, G, R) color tuple for OpenCV
        """
        # Normalize speed 0-1
        norm_speed = min(speed / max_speed, 1.0)
        
        # Interpolate: blue (0,0,255) to red (255,0,0)
        red = int(255 * norm_speed)
        blue = int(255 * (1 - norm_speed))
        green = 0
        
        return (blue, green, red)
    
    def reset(self):
        """Reset tracker"""
        self.tracks = []
        self.next_id = 0
        self.track_history.clear()
        self.track_colors.clear()
