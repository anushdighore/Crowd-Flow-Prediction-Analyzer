"""
Occupancy Processing Module
Integrates occupancy monitoring with existing ML pipeline.
Processes count data and enriches results with occupancy information.
"""

from typing import Dict, Optional, Any, List
import cv2
import numpy as np
import base64
from datetime import datetime
import json
from occupancy_monitor import OccupancyMonitor
from occupancy_config import OccupancyConfig


class OccupancyProcessor:
    """
    Processes ML results and enriches them with occupancy data.
    
    Features:
    - Integrates with existing count pipeline
    - Manages multiple concurrent streams
    - Enriches ML results with occupancy metrics
    - Handles configuration updates
    - Generates density heatmaps
    - Real-time alert system
    - Historical data tracking
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize OccupancyProcessor.
        
        Args:
            config_dir: Directory for configuration files
        """
        self.config_manager = OccupancyConfig(config_dir)
        self.monitors: Dict[str, OccupancyMonitor] = {}
        self.historical_data: Dict[str, List[Dict]] = {}  # Store historical data per stream
        self.max_historical_points = 1000  # Limit historical data storage
    
    def get_or_create_monitor(self, stream_id: str) -> OccupancyMonitor:
        """
        Get existing monitor or create new one for stream.
        
        Args:
            stream_id: Unique stream identifier
            
        Returns:
            OccupancyMonitor instance
        """
        if stream_id not in self.monitors:
            config = self.config_manager.get_stream_config(stream_id)
            self.monitors[stream_id] = OccupancyMonitor(
                max_capacity=config["max_capacity"],
                alert_threshold=config["alert_threshold"],
                reset_threshold=config["reset_threshold"],
                window_size_seconds=config["window_size_seconds"]
            )
            
            # Initialize historical data for this stream
            if stream_id not in self.historical_data:
                self.historical_data[stream_id] = []
        
        return self.monitors[stream_id]
    
    def generate_density_heatmap(self, density_map: np.ndarray, frame_shape: tuple) -> Optional[str]:
        """
        Generate colored heatmap from density map.
        
        Args:
            density_map: Raw density map from ML model
            frame_shape: Original frame dimensions (height, width)
            
        Returns:
            Base64 encoded heatmap image or None if failed
        """
        try:
            if density_map is None:
                return None
                
            # Normalize density map to 0-255 range
            if density_map.max() > 0:
                normalized = ((density_map - density_map.min()) / 
                            (density_map.max() - density_map.min()) * 255).astype(np.uint8)
            else:
                normalized = np.zeros_like(density_map, dtype=np.uint8)
            
            # Apply colormap (jet for good density visualization)
            colored_heatmap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
            
            # Resize to original frame dimensions
            if colored_heatmap.shape[:2] != frame_shape:
                colored_heatmap = cv2.resize(colored_heatmap, (frame_shape[1], frame_shape[0]))
            
            # Add transparency overlay effect
            alpha = 0.6  # Transparency level
            
            # Encode to base64
            _, buffer = cv2.imencode('.png', colored_heatmap)
            heatmap_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return f"data:image/png;base64,{heatmap_base64}"
            
        except Exception as e:
            print(f"Error generating density heatmap: {e}")
            return None
    
    def check_occupancy_alerts(self, stream_id: str, current_count: int, current_percentage: float) -> List[Dict]:
        """
        Check and generate occupancy alerts.
        
        Args:
            stream_id: Stream identifier
            current_count: Current person count
            current_percentage: Current occupancy percentage
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        monitor = self.monitors.get(stream_id)
        
        if not monitor:
            return alerts
            
        # Check alert threshold
        if current_percentage >= monitor.alert_threshold:
            alerts.append({
                'type': 'occupancy_alert',
                'level': 'warning' if current_percentage < 90 else 'critical',
                'message': f'Occupancy at {current_percentage:.1f}% ({current_count}/{monitor.max_capacity})',
                'threshold': monitor.alert_threshold,
                'current_percentage': current_percentage,
                'timestamp': datetime.now().isoformat(),
                'stream_id': stream_id
            })
        
        # Check reset threshold (for alert recovery)
        elif current_percentage <= monitor.reset_threshold and monitor.alert_triggered:
            alerts.append({
                'type': 'occupancy_reset',
                'level': 'info',
                'message': f'Occupancy normalized to {current_percentage:.1f}%',
                'reset_threshold': monitor.reset_threshold,
                'current_percentage': current_percentage,
                'timestamp': datetime.now().isoformat(),
                'stream_id': stream_id
            })
        
        return alerts
    
    def add_historical_data_point(self, stream_id: str, count: int, percentage: float, 
                                density_map: Optional[np.ndarray] = None):
        """
        Add historical data point for tracking and analytics.
        
        Args:
            stream_id: Stream identifier
            count: Person count
            percentage: Occupancy percentage
            density_map: Optional density map for visualization
        """
        if stream_id not in self.historical_data:
            self.historical_data[stream_id] = []
        
        data_point = {
            'timestamp': datetime.now().isoformat(),
            'count': count,
            'percentage': percentage,
            'stream_id': stream_id
        }
        
        # Add density heatmap if available
        if density_map is not None:
            # Generate heatmap for this data point
            frame_shape = density_map.shape
            heatmap_base64 = self.generate_density_heatmap(density_map, frame_shape)
            if heatmap_base64:
                data_point['density_heatmap'] = heatmap_base64
        
        # Add to historical data
        self.historical_data[stream_id].append(data_point)
        
        # Limit storage to prevent memory issues
        if len(self.historical_data[stream_id]) > self.max_historical_points:
            self.historical_data[stream_id] = self.historical_data[stream_id][-self.max_historical_points:]
    
    def get_historical_data(self, stream_id: str, limit: int = 100) -> List[Dict]:
        """
        Get historical data for a stream.
        
        Args:
            stream_id: Stream identifier
            limit: Maximum number of data points to return
            
        Returns:
            List of historical data points
        """
        if stream_id not in self.historical_data:
            return []
        
        return self.historical_data[stream_id][-limit:]
    
    def get_occupancy_statistics(self, stream_id: str) -> Dict:
        """
        Get occupancy statistics for a stream.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Dictionary with occupancy statistics
        """
        historical = self.get_historical_data(stream_id)
        
        if not historical:
            return {
                'peak_count': 0,
                'peak_percentage': 0.0,
                'average_count': 0.0,
                'average_percentage': 0.0,
                'data_points': 0
            }
        
        counts = [point['count'] for point in historical]
        percentages = [point['percentage'] for point in historical]
        
        return {
            'peak_count': max(counts),
            'peak_percentage': max(percentages),
            'average_count': sum(counts) / len(counts),
            'average_percentage': sum(percentages) / len(percentages),
            'data_points': len(historical),
            'time_range': {
                'start': historical[0]['timestamp'],
                'end': historical[-1]['timestamp']
            }
        }
    
    def process_count(self, stream_id: str, current_count: int, density_map: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Process count data and return enriched occupancy status.
        
        Args:
            stream_id: Unique stream identifier
            current_count: Current person count from ML model
            density_map: Optional density map for visualization
            
        Returns:
            Dictionary with occupancy information
        """
        # Get or create monitor for this stream
        monitor = self.get_or_create_monitor(stream_id)
        
        # Update count
        monitor.update_count(current_count)
        
        # Get occupancy status
        occupancy_status = monitor.get_occupancy_status()
        
        # Get current percentage for alerts
        current_percentage = occupancy_status.get('percentage', 0.0)
        
        # Generate alerts
        alerts = self.check_occupancy_alerts(stream_id, current_count, current_percentage)
        
        # Add historical data point
        self.add_historical_data_point(stream_id, current_count, current_percentage, density_map)
        
        # Generate density heatmap if available
        density_heatmap = None
        if density_map is not None:
            frame_shape = density_map.shape
            density_heatmap = self.generate_density_heatmap(density_map, frame_shape)
        
        # Get statistics
        statistics = self.get_occupancy_statistics(stream_id)
        
        # Enhanced occupancy status
        enhanced_status = occupancy_status.copy()
        enhanced_status.update({
            'alerts': alerts,
            'density_heatmap': density_heatmap,
            'statistics': statistics,
            'historical_count': len(self.historical_data.get(stream_id, [])),
            'stream_id': stream_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return enhanced_status
    
    def process_ml_result(
        self,
        stream_id: str,
        ml_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich ML result with occupancy data.
        
        Args:
            stream_id: Unique stream identifier
            ml_result: Original ML model result
            
        Returns:
            Enhanced result with occupancy information
        """
        # Extract count from ML result
        current_count = ml_result.get("count", 0)
        
        # Extract density map if available (from CSRNet/VMamba)
        density_map = ml_result.get("density_map")
        
        # Process count through occupancy monitor with enhanced features
        occupancy_status = self.process_count(stream_id, current_count, density_map)
        
        # Enrich ML result
        enriched_result = ml_result.copy()
        enriched_result["occupancy"] = occupancy_status
        
        # Add enhanced occupancy-specific fields
        enriched_result.update({
            "occupancy_alerts": occupancy_status.get("alerts", []),
            "density_heatmap": occupancy_status.get("density_heatmap"),
            "occupancy_statistics": occupancy_status.get("statistics", {}),
            "historical_data_available": len(self.historical_data.get(stream_id, [])) > 0
        })
        
        return enriched_result
    
    def get_occupancy_status(self, stream_id: str) -> Optional[Dict]:
        """
        Get current occupancy status for a stream.
        
        Args:
            stream_id: Unique stream identifier
            
        Returns:
            Occupancy status dictionary or None if stream not found
        """
        if stream_id in self.monitors:
            return self.monitors[stream_id].get_occupancy_status()
        return None
    
    def get_alert_info(self, stream_id: str) -> Optional[Dict]:
        """
        Get alert information for a stream.
        
        Args:
            stream_id: Unique stream identifier
            
        Returns:
            Alert information dictionary or None if stream not found
        """
        if stream_id in self.monitors:
            return self.monitors[stream_id].get_alert_info()
        return None
    
    def update_stream_config(self, stream_id: str, config_updates: Dict) -> bool:
        """
        Update configuration for a specific stream.
        
        Args:
            stream_id: Unique stream identifier
            config_updates: Configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        # Validate and save configuration
        if not self.config_manager.update_stream_config(stream_id, config_updates):
            return False
        
        # Update monitor if it exists
        if stream_id in self.monitors:
            monitor = self.monitors[stream_id]
            monitor.update_config(
                max_capacity=config_updates.get("max_capacity"),
                alert_threshold=config_updates.get("alert_threshold"),
                reset_threshold=config_updates.get("reset_threshold"),
                window_size_seconds=config_updates.get("window_size_seconds")
            )
        
        return True
    
    def reset_stream(self, stream_id: str) -> None:
        """
        Reset monitor for a stream.
        
        Args:
            stream_id: Unique stream identifier
        """
        if stream_id in self.monitors:
            self.monitors[stream_id].clear_history()
            self.monitors[stream_id].reset_alert()
    
    def remove_stream(self, stream_id: str) -> None:
        """
        Remove monitor for a stream.
        
        Args:
            stream_id: Unique stream identifier
        """
        if stream_id in self.monitors:
            del self.monitors[stream_id]
    
    def get_all_streams_status(self) -> Dict[str, Dict]:
        """
        Get occupancy status for all active streams.
        
        Returns:
            Dictionary mapping stream_id to occupancy status
        """
        return {
            stream_id: monitor.get_occupancy_status()
            for stream_id, monitor in self.monitors.items()
        }
    
    def get_active_alerts(self) -> Dict[str, Dict]:
        """
        Get all active alerts across streams.
        
        Returns:
            Dictionary mapping stream_id to alert info for streams with active alerts
        """
        return {
            stream_id: monitor.get_alert_info()
            for stream_id, monitor in self.monitors.items()
            if monitor.alert_state
        }
    
    def update_global_config(self, config_updates: Dict) -> bool:
        """
        Update global configuration (applies to new streams).
        
        Args:
            config_updates: Configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        return self.config_manager.update_config(config_updates)
    
    def get_config(self) -> Dict:
        """
        Get current global configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config_manager.get_config()
