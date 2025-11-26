"""
Occupancy Monitoring Module
Handles sliding window calculations, alert state management, and occupancy percentage computation.
"""

from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple


class OccupancyMonitor:
    """
    Monitors occupancy levels with sliding window averaging and alert state management.
    
    Features:
    - Sliding window average over configurable time period (3-5 seconds)
    - Alert triggering at 80% occupancy threshold
    - Alert reset at 78% occupancy threshold (hysteresis to prevent flapping)
    - Real-time occupancy percentage calculation
    """
    
    def __init__(
        self,
        max_capacity: int,
        alert_threshold: float = 80.0,
        reset_threshold: float = 78.0,
        window_size_seconds: float = 3.0
    ):
        """
        Initialize OccupancyMonitor.
        
        Args:
            max_capacity: Maximum capacity of the space
            alert_threshold: Occupancy percentage to trigger alert (default 80%)
            reset_threshold: Occupancy percentage to reset alert (default 78%)
            window_size_seconds: Sliding window size in seconds (default 3.0)
        """
        self.max_capacity = max_capacity
        self.alert_threshold = alert_threshold
        self.reset_threshold = reset_threshold
        self.window_size_seconds = window_size_seconds
        
        # Sliding window buffer: (timestamp, count)
        self.count_history: deque = deque()
        
        # Alert state management
        self.alert_state = False
        self.alert_triggered = False
        self.last_alert_time: Optional[datetime] = None
        
        # Statistics
        self.current_count = 0
        self.occupancy_percentage = 0.0
        self.average_count = 0.0
    
    def update_count(self, current_count: int) -> None:
        """
        Update the count and maintain sliding window.
        
        Args:
            current_count: Current person count from ML model
        """
        now = datetime.now()
        self.current_count = current_count
        
        # Add new count to history
        self.count_history.append((now, current_count))
        
        # Remove old entries outside the window
        cutoff_time = now - timedelta(seconds=self.window_size_seconds)
        while self.count_history and self.count_history[0][0] < cutoff_time:
            self.count_history.popleft()
        
        # Update statistics
        self._compute_occupancy()
        self._update_alert_state()
    
    def _compute_occupancy(self) -> None:
        """Compute occupancy percentage using sliding window average."""
        if not self.count_history:
            self.average_count = 0.0
            self.occupancy_percentage = 0.0
            return
        
        # Calculate average count in the window
        total_count = sum(count for _, count in self.count_history)
        self.average_count = total_count / len(self.count_history)
        
        # Calculate occupancy percentage
        self.occupancy_percentage = (self.average_count / self.max_capacity) * 100.0
    
    def _update_alert_state(self) -> None:
        """
        Update alert state based on occupancy percentage.
        Uses hysteresis to prevent alert flapping.
        """
        self.alert_triggered = False
        
        if self.occupancy_percentage >= self.alert_threshold:
            # Trigger alert if not already in alert state
            if not self.alert_state:
                self.alert_state = True
                self.alert_triggered = True
                self.last_alert_time = datetime.now()
        
        elif self.occupancy_percentage < self.reset_threshold:
            # Reset alert state
            if self.alert_state:
                self.alert_state = False
    
    def get_occupancy_status(self) -> Dict:
        """
        Get current occupancy status.
        
        Returns:
            Dictionary containing:
            - current_count: Current person count
            - average_count: Sliding window average count
            - occupancy_percentage: Occupancy as percentage
            - alert_state: Boolean indicating if alert is active
            - alert_triggered: Boolean indicating if alert just triggered
            - max_capacity: Maximum capacity
            - timestamp: Current timestamp
        """
        return {
            "current_count": self.current_count,
            "average_count": round(self.average_count, 2),
            "occupancy_percentage": round(self.occupancy_percentage, 2),
            "alert_state": self.alert_state,
            "alert_triggered": self.alert_triggered,
            "max_capacity": self.max_capacity,
            "timestamp": datetime.now().isoformat(),
            "window_size_seconds": self.window_size_seconds,
            "alert_threshold": self.alert_threshold,
            "reset_threshold": self.reset_threshold
        }
    
    def get_alert_info(self) -> Dict:
        """
        Get alert-specific information.
        
        Returns:
            Dictionary containing alert details
        """
        return {
            "alert_active": self.alert_state,
            "alert_triggered": self.alert_triggered,
            "last_alert_time": self.last_alert_time.isoformat() if self.last_alert_time else None,
            "occupancy_percentage": round(self.occupancy_percentage, 2),
            "alert_threshold": self.alert_threshold,
            "reset_threshold": self.reset_threshold
        }
    
    def reset_alert(self) -> None:
        """Manually reset alert state."""
        self.alert_state = False
        self.alert_triggered = False
    
    def clear_history(self) -> None:
        """Clear count history."""
        self.count_history.clear()
        self.average_count = 0.0
        self.occupancy_percentage = 0.0
    
    def update_config(
        self,
        max_capacity: Optional[int] = None,
        alert_threshold: Optional[float] = None,
        reset_threshold: Optional[float] = None,
        window_size_seconds: Optional[float] = None
    ) -> None:
        """
        Update configuration parameters.
        
        Args:
            max_capacity: New maximum capacity
            alert_threshold: New alert threshold percentage
            reset_threshold: New reset threshold percentage
            window_size_seconds: New window size in seconds
        """
        if max_capacity is not None:
            self.max_capacity = max_capacity
        if alert_threshold is not None:
            self.alert_threshold = alert_threshold
        if reset_threshold is not None:
            self.reset_threshold = reset_threshold
        if window_size_seconds is not None:
            self.window_size_seconds = window_size_seconds
        
        # Recompute with new config
        self._compute_occupancy()
        self._update_alert_state()
