"""
Occupancy Configuration Management
Handles loading, saving, and managing occupancy system configuration.
"""

import json
import os
from typing import Dict, Optional
from datetime import datetime


class OccupancyConfig:
    """
    Manages occupancy system configuration.
    
    Features:
    - Load/save configuration from JSON
    - Default configuration values
    - Configuration validation
    - Per-stream configuration management
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        "max_capacity": 100,
        "alert_threshold": 80.0,
        "reset_threshold": 78.0,
        "window_size_seconds": 3.0,
        "enabled": True,
        "alert_enabled": True
    }
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize OccupancyConfig.
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "occupancy_config.json")
        
        # Create config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Load or create default configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """
        Load configuration from file or create default.
        
        Returns:
            Configuration dictionary
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.DEFAULT_CONFIG, **config}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self._save_config(self.DEFAULT_CONFIG.copy())
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_config(self) -> Dict:
        """
        Get current configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def update_config(self, updates: Dict) -> bool:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary with configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        # Validate updates
        if not self._validate_config(updates):
            return False
        
        # Update configuration
        self.config.update(updates)
        
        # Save to file
        return self._save_config(self.config)
    
    def _validate_config(self, config: Dict) -> bool:
        """
        Validate configuration values.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Validate max_capacity
        if "max_capacity" in config:
            if not isinstance(config["max_capacity"], int) or config["max_capacity"] <= 0:
                print("Invalid max_capacity: must be positive integer")
                return False
        
        # Validate thresholds
        if "alert_threshold" in config:
            if not isinstance(config["alert_threshold"], (int, float)) or not (0 <= config["alert_threshold"] <= 100):
                print("Invalid alert_threshold: must be between 0 and 100")
                return False
        
        if "reset_threshold" in config:
            if not isinstance(config["reset_threshold"], (int, float)) or not (0 <= config["reset_threshold"] <= 100):
                print("Invalid reset_threshold: must be between 0 and 100")
                return False
        
        # Validate window size
        if "window_size_seconds" in config:
            if not isinstance(config["window_size_seconds"], (int, float)) or config["window_size_seconds"] <= 0:
                print("Invalid window_size_seconds: must be positive number")
                return False
        
        # Validate threshold relationship
        if "alert_threshold" in config and "reset_threshold" in config:
            if config["reset_threshold"] >= config["alert_threshold"]:
                print("Invalid thresholds: reset_threshold must be less than alert_threshold")
                return False
        
        return True
    
    def get_stream_config(self, stream_id: str) -> Dict:
        """
        Get configuration for a specific stream.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Configuration dictionary for the stream
        """
        stream_config_file = os.path.join(self.config_dir, f"occupancy_{stream_id}.json")
        
        if os.path.exists(stream_config_file):
            try:
                with open(stream_config_file, 'r') as f:
                    stream_config = json.load(f)
                    return {**self.config, **stream_config}
            except (json.JSONDecodeError, IOError):
                return self.config.copy()
        else:
            return self.config.copy()
    
    def update_stream_config(self, stream_id: str, updates: Dict) -> bool:
        """
        Update configuration for a specific stream.
        
        Args:
            stream_id: Stream identifier
            updates: Configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        if not self._validate_config(updates):
            return False
        
        stream_config_file = os.path.join(self.config_dir, f"occupancy_{stream_id}.json")
        
        try:
            with open(stream_config_file, 'w') as f:
                json.dump(updates, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving stream config: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to defaults.
        
        Returns:
            True if successful, False otherwise
        """
        self.config = self.DEFAULT_CONFIG.copy()
        return self._save_config(self.config)
    
    def get_config_info(self) -> Dict:
        """
        Get information about current configuration.
        
        Returns:
            Dictionary with configuration metadata
        """
        return {
            "config": self.config.copy(),
            "config_file": self.config_file,
            "last_modified": datetime.fromtimestamp(
                os.path.getmtime(self.config_file)
            ).isoformat() if os.path.exists(self.config_file) else None
        }
