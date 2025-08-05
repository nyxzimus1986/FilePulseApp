"""
Configuration management for FilePulseApp.

This module handles loading, saving, and managing configuration settings
for the file monitoring application.
"""

import json
import os
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for FilePulseApp."""
    
    DEFAULT_CONFIG = {
        "monitoring": {
            "watch_directories": [],
            "file_extensions": [".txt", ".log", ".json", ".xml", ".csv"],
            "recursive": True,
            "ignore_hidden": True
        },
        "filtering": {
            "show_system_changes": True,
            "show_user_changes": True,
            "separate_system_user": True,
            "system_change_color": "#888888",
            "user_change_color": "#000000",
            "system_file_patterns": [
                "thumbs.db", "desktop.ini", ".ds_store", "~$", ".tmp", 
                ".temp", ".swp", ".bak", ".cache", ".log", ".pid", ".lock"
            ],
            "system_directories": [
                "appdata", "programdata", "windows", "system32", 
                "program files", "recycle", "temp", "tmp", "__pycache__",
                ".vscode", ".idea", ".git", ".svn"
            ]
        },
        "gui": {
            "theme": "default",
            "window_size": [800, 600],
            "splash_enabled": True,
            "splash_duration": 3000
        },
        "output": {
            "log_level": "INFO",
            "log_file": "filepulse.log",
            "console_output": True
        },
        "advanced": {
            "buffer_size": 1000,
            "polling_interval": 1.0,
            "max_file_size": "10MB"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        return os.path.join(os.path.expanduser("~"), ".filepulse", "config.json")
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge_config(self.config, user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                print("Using default configuration.")
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error: Failed to save config to {self.config_path}: {e}")
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> None:
        """Recursively merge user configuration with defaults."""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def get(self, section: str, key: str = None) -> Any:
        """Get configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key name (optional)
            
        Returns:
            Configuration value or section
        """
        if key is None:
            return self.config.get(section, {})
        return self.config.get(section, {}).get(key)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def get_watch_directories(self) -> list:
        """Get list of directories to monitor."""
        return self.get("monitoring", "watch_directories")
    
    def add_watch_directory(self, directory: str) -> None:
        """Add directory to watch list."""
        directories = self.get_watch_directories()
        if directory not in directories:
            directories.append(directory)
            self.set("monitoring", "watch_directories", directories)
    
    def remove_watch_directory(self, directory: str) -> None:
        """Remove directory from watch list."""
        directories = self.get_watch_directories()
        if directory in directories:
            directories.remove(directory)
            self.set("monitoring", "watch_directories", directories)
