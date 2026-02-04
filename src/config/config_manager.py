"""
Configuration Manager
Handles loading, saving, and accessing configuration
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages application configuration"""

    DEFAULT_CONFIG = {
        "images": {
            "normal_dir": "",
            "wait_image": "",
            "timeout_dir": ""
        },
        "window": {
            "remember_position": True,
            "always_on_top": True,
            "last_x": 100,
            "last_y": 100,
            "last_width": 1280,
            "last_height": 720
        },
        "timeout": {
            "default_duration": 10,
            "show_countdown": True,
            "countdown_seconds": 5
        },
        "batch": {
            "default_count": 6,
            "cycling_enabled": False,
            "cycling_sequence": "1,2,3,4,5,6"
        },
        "lag_duration": 3,
        "log_file": "",
        "report_dir": "",
        "tray": {
            "enabled": True,
            "minimize_to_tray": True
        }
    }

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        """Ensure all default values are present"""
        merged = self.DEFAULT_CONFIG.copy()
        merged.update(self._config)
        self._config = merged

    def load(self) -> bool:
        """Load configuration from file"""
        if not self.config_path.exists():
            return False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                self._config = self.DEFAULT_CONFIG.copy()
                self._config.update(loaded)
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return False

    def save(self) -> bool:
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    @property
    def is_configured(self) -> bool:
        """Check if required configuration is present"""
        return bool(
            self.get('images.normal_dir') and
            self.get('images.wait_image') and
            self.get('images.timeout_dir')
        )

    def get_normal_dir(self) -> Optional[Path]:
        """Get normal images directory"""
        path = self.get('images.normal_dir')
        return Path(path) if path else None

    def get_wait_image(self) -> Optional[Path]:
        """Get wait image path"""
        path = self.get('images.wait_image')
        return Path(path) if path else None

    def get_timeout_dir(self) -> Optional[Path]:
        """Get timeout images directory"""
        path = self.get('images.timeout_dir')
        return Path(path) if path else None

    def get_log_file(self) -> Path:
        """Get log file path"""
        path = self.get('log_file')
        if path:
            return Path(path)
        # Default to logs directory
        return Path("logs/preview_pc.log")

    def get_report_dir(self) -> Path:
        """Get report directory path"""
        path = self.get('report_dir')
        if path:
            return Path(path)
        return Path("reports/")
