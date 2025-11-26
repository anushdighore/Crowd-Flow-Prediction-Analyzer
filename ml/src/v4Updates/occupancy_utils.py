"""
Occupancy Utilities Module
Helper functions for occupancy monitoring and alert generation.
"""

from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlidingWindowCalculator:
    """Utility for sliding window calculations."""
    
    @staticmethod
    def calculate_average(
        values: List[Tuple[datetime, float]],
        window_seconds: float
    ) -> float:
        """
        Calculate average of values within sliding window.
        
        Args:
            values: List of (timestamp, value) tuples
            window_seconds: Window size in seconds
            
        Returns:
            Average value in window
        """
        if not values:
            return 0.0
        
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=window_seconds)
        
        window_values = [v for t, v in values if t >= cutoff_time]
        
        if not window_values:
            return 0.0
        
        return sum(window_values) / len(window_values)
    
    @staticmethod
    def calculate_trend(
        values: List[Tuple[datetime, float]],
        window_seconds: float
    ) -> str:
        """
        Calculate trend of values in sliding window.
        
        Args:
            values: List of (timestamp, value) tuples
            window_seconds: Window size in seconds
            
        Returns:
            Trend: "increasing", "decreasing", or "stable"
        """
        if len(values) < 2:
            return "stable"
        
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=window_seconds)
        
        window_values = [(t, v) for t, v in values if t >= cutoff_time]
        
        if len(window_values) < 2:
            return "stable"
        
        # Compare first and last values
        first_value = window_values[0][1]
        last_value = window_values[-1][1]
        
        threshold = 0.05 * first_value if first_value > 0 else 1
        
        if last_value > first_value + threshold:
            return "increasing"
        elif last_value < first_value - threshold:
            return "decreasing"
        else:
            return "stable"


class AlertGenerator:
    """Utility for generating alert events."""
    
    @staticmethod
    def create_alert_event(
        stream_id: str,
        occupancy_percentage: float,
        max_capacity: int,
        current_count: int,
        alert_type: str = "occupancy"
    ) -> Dict[str, Any]:
        """
        Create alert event.
        
        Args:
            stream_id: Stream identifier
            occupancy_percentage: Current occupancy percentage
            max_capacity: Maximum capacity
            current_count: Current person count
            alert_type: Type of alert
            
        Returns:
            Alert event dictionary
        """
        return {
            "event_type": "alert",
            "alert_type": alert_type,
            "stream_id": stream_id,
            "timestamp": datetime.now().isoformat(),
            "occupancy_percentage": round(occupancy_percentage, 2),
            "max_capacity": max_capacity,
            "current_count": current_count,
            "severity": AlertGenerator._calculate_severity(occupancy_percentage)
        }
    
    @staticmethod
    def _calculate_severity(occupancy_percentage: float) -> str:
        """
        Calculate alert severity based on occupancy percentage.
        
        Args:
            occupancy_percentage: Occupancy percentage
            
        Returns:
            Severity level: "low", "medium", "high", "critical"
        """
        if occupancy_percentage >= 95:
            return "critical"
        elif occupancy_percentage >= 90:
            return "high"
        elif occupancy_percentage >= 80:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def create_status_update(
        stream_id: str,
        occupancy_status: Dict
    ) -> Dict[str, Any]:
        """
        Create status update event.
        
        Args:
            stream_id: Stream identifier
            occupancy_status: Occupancy status dictionary
            
        Returns:
            Status update event dictionary
        """
        return {
            "event_type": "status_update",
            "stream_id": stream_id,
            "timestamp": datetime.now().isoformat(),
            "occupancy": occupancy_status
        }


class ConfigValidator:
    """Utility for validating occupancy configuration."""
    
    @staticmethod
    def validate_capacity(max_capacity: int) -> Tuple[bool, str]:
        """
        Validate maximum capacity value.
        
        Args:
            max_capacity: Maximum capacity value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(max_capacity, int):
            return False, "max_capacity must be an integer"
        
        if max_capacity <= 0:
            return False, "max_capacity must be positive"
        
        if max_capacity > 10000:
            return False, "max_capacity seems unreasonably high"
        
        return True, ""
    
    @staticmethod
    def validate_thresholds(
        alert_threshold: float,
        reset_threshold: float
    ) -> Tuple[bool, str]:
        """
        Validate alert thresholds.
        
        Args:
            alert_threshold: Alert trigger threshold (0-100)
            reset_threshold: Alert reset threshold (0-100)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(alert_threshold, (int, float)):
            return False, "alert_threshold must be a number"
        
        if not isinstance(reset_threshold, (int, float)):
            return False, "reset_threshold must be a number"
        
        if not (0 <= alert_threshold <= 100):
            return False, "alert_threshold must be between 0 and 100"
        
        if not (0 <= reset_threshold <= 100):
            return False, "reset_threshold must be between 0 and 100"
        
        if reset_threshold >= alert_threshold:
            return False, "reset_threshold must be less than alert_threshold"
        
        return True, ""
    
    @staticmethod
    def validate_window_size(window_size_seconds: float) -> Tuple[bool, str]:
        """
        Validate sliding window size.
        
        Args:
            window_size_seconds: Window size in seconds
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(window_size_seconds, (int, float)):
            return False, "window_size_seconds must be a number"
        
        if window_size_seconds <= 0:
            return False, "window_size_seconds must be positive"
        
        if window_size_seconds > 60:
            return False, "window_size_seconds seems too large"
        
        return True, ""


class OccupancyLogger:
    """Utility for logging occupancy events."""
    
    @staticmethod
    def log_alert(
        stream_id: str,
        occupancy_percentage: float,
        alert_info: Dict
    ) -> None:
        """
        Log alert event.
        
        Args:
            stream_id: Stream identifier
            occupancy_percentage: Current occupancy percentage
            alert_info: Alert information
        """
        logger.warning(
            f"ALERT: Stream {stream_id} - Occupancy {occupancy_percentage}% "
            f"(Threshold: {alert_info['alert_threshold']}%)"
        )
    
    @staticmethod
    def log_status(
        stream_id: str,
        occupancy_status: Dict
    ) -> None:
        """
        Log occupancy status.
        
        Args:
            stream_id: Stream identifier
            occupancy_status: Occupancy status dictionary
        """
        logger.info(
            f"Stream {stream_id} - Count: {occupancy_status['current_count']}, "
            f"Occupancy: {occupancy_status['occupancy_percentage']}%, "
            f"Alert: {occupancy_status['alert_state']}"
        )
    
    @staticmethod
    def log_config_update(
        stream_id: str,
        config_updates: Dict
    ) -> None:
        """
        Log configuration update.
        
        Args:
            stream_id: Stream identifier
            config_updates: Configuration updates
        """
        logger.info(
            f"Stream {stream_id} - Config updated: {config_updates}"
        )
