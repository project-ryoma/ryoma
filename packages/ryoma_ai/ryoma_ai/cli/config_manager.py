"""
Configuration Manager for Ryoma AI CLI

Handles loading, saving, and managing configuration settings.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manages configuration loading, saving, and validation."""

    def __init__(self, config_file: str = None):
        """
        Initialize the configuration manager.

        Args:
            config_file: Optional path to config file. Defaults to ~/.ryoma/config.json
        """
        self.config_file = (
            Path(config_file) if config_file else Path.home() / ".ryoma" / "config.json"
        )
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")

        # Return default configuration
        return {
            "model": "gpt-4o",
            "mode": "enhanced",
            "database": {
                "type": "postgres",
                "host": "localhost",
                "port": 5432,
                "database": "postgres",
                "user": os.environ.get("POSTGRES_USER", ""),
                "password": os.environ.get("POSTGRES_PASSWORD", ""),
            },
            "agent": {
                "auto_approve_all": False,
                "retry_count": 3,
                "timeout_seconds": 300,
            },
        }

    def save_config(self) -> None:
        """Save current configuration to file."""
        # Ensure config directory exists
        self.config_file.parent.mkdir(exist_ok=True)

        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def update_config(self, key: str, value: Any) -> None:
        """
        Update a configuration value and save.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: New value
        """
        keys = key.split(".")
        config_ref = self.config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]

        # Set the value
        config_ref[keys[-1]] = value
        self.save_config()

    def get_config(self, key: str = None, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key doesn't exist

        Returns:
            Configuration value or entire config if key is None
        """
        if key is None:
            return self.config

        keys = key.split(".")
        config_ref = self.config

        try:
            for k in keys:
                config_ref = config_ref[k]
            return config_ref
        except (KeyError, TypeError):
            return default
