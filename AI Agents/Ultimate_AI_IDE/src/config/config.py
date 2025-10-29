"""
Configuration Manager

Manages application configuration loading and access.
"""

import json
import os
from typing import Any, Optional, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration manager for UAIDE.
    
    Loads and manages configuration from JSON files with support
    for defaults and environment variables.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or "config.json"
        self.config_data: Dict[str, Any] = {}
        self._defaults = self._get_defaults()
        
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "ai": {
                "model_path": "models/llama-3-8b-q4.gguf",
                "max_tokens": 2048,
                "temperature": 0.7,
                "context_length": 8192,
                "gpu_layers": 0
            },
            "database": {
                "path": "data/uaide.db",
                "backup_enabled": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/uaide.log"
            },
            "code_generation": {
                "max_file_length": 500,
                "auto_format": True
            }
        }
        
    def load(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if successful
        """
        try:
            config_file = Path(self.config_path)
            
            # If config doesn't exist, try config.example.json
            if not config_file.exists():
                example_config = Path("config.example.json")
                if example_config.exists():
                    logger.info(f"Config not found, using {example_config}")
                    config_file = example_config
                else:
                    logger.warning("No config file found, using defaults")
                    self.config_data = self._defaults.copy()
                    return True
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            
            # Merge with defaults for missing keys
            self._merge_defaults()
            
            # Expand environment variables
            self._expand_env_vars()
            
            logger.info(f"Configuration loaded from {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config_data = self._defaults.copy()
            return False
    
    def _merge_defaults(self) -> None:
        """Merge defaults for missing configuration keys."""
        def merge_dict(target: dict, source: dict) -> None:
            for key, value in source.items():
                if key not in target:
                    target[key] = value
                elif isinstance(value, dict) and isinstance(target[key], dict):
                    merge_dict(target[key], value)
        
        merge_dict(self.config_data, self._defaults)
    
    def _expand_env_vars(self) -> None:
        """Expand environment variables in string values."""
        def expand_dict(d: dict) -> None:
            for key, value in d.items():
                if isinstance(value, str):
                    d[key] = os.path.expandvars(value)
                elif isinstance(value, dict):
                    expand_dict(value)
        
        expand_dict(self.config_data)
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'ai.model_path')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
        
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'ai.temperature')
            value: Value to set
        """
        keys = key.split('.')
        target = self.config_data
        
        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # Set the value
        target[keys[-1]] = value
        
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            path: Optional path to save to (defaults to config_path)
            
        Returns:
            True if successful
        """
        try:
            save_path = Path(path or self.config_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration data.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config_data.copy()
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.config_data = self._defaults.copy()
        logger.info("Configuration reset to defaults")
