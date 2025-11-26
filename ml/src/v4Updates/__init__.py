"""
V4 Updates - Occupancy Monitoring System
Provides occupancy monitoring, alert generation, and configuration management.
"""

from .occupancy_monitor import OccupancyMonitor
from .occupancy_config import OccupancyConfig
from .occupancy_processor import OccupancyProcessor
from .occupancy_utils import (
    SlidingWindowCalculator,
    AlertGenerator,
    ConfigValidator,
    OccupancyLogger
)

__all__ = [
    "OccupancyMonitor",
    "OccupancyConfig",
    "OccupancyProcessor",
    "SlidingWindowCalculator",
    "AlertGenerator",
    "ConfigValidator",
    "OccupancyLogger"
]

__version__ = "4.0.0"
__description__ = "Occupancy Monitoring System for Crowd Flow Prediction"
