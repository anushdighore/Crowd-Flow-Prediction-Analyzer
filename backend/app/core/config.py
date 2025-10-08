"""
Configuration loader for YAML files
Reads from config/ directory and provides access to settings
"""
import yaml
from pathlib import Path
from typing import Dict, Any
from functools import lru_cache


class ConfigLoader:
    """Load and manage YAML configuration files"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Any] = {}
    
    def load(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file
        
        Args:
            filename: Name of the config file (e.g., 'config.yaml')
            
        Returns:
            Dictionary containing configuration
        """
        if filename in self._cache:
            return self._cache[filename]
        
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self._cache[filename] = config
        return config
    
    def get(self, filename: str, key_path: str, default: Any = None) -> Any:
        """
        Get a specific value from config using dot notation
        
        Args:
            filename: Config file name
            key_path: Dot-separated path (e.g., 'data.image.input_size')
            default: Default value if key not found
            
        Returns:
            Configuration value
            
        Example:
            >>> config = ConfigLoader()
            >>> config.get('config.yaml', 'data.image.input_size')
            [512, 512]
        """
        config = self.load(filename)
        
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value


@lru_cache()
def get_config_loader(config_dir: str = "config") -> ConfigLoader:
    """Get cached ConfigLoader instance"""
    return ConfigLoader(config_dir)


# Convenience functions
def load_config(filename: str = "config.yaml") -> Dict[str, Any]:
    """Load main configuration file"""
    loader = get_config_loader()
    return loader.load(filename)


def get_config_value(key_path: str, default: Any = None, filename: str = "config.yaml") -> Any:
    """Get specific config value using dot notation"""
    loader = get_config_loader()
    return loader.get(filename, key_path, default)
