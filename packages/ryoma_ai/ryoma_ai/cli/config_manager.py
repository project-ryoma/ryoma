"""
Configuration Manager for Ryoma AI CLI

Handles loading, saving, and managing configuration settings.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ryoma_ai.store.config import StoreConfig
from ryoma_ai.vector_store.config import VectorStoreConfig


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

        # Return default configuration with separate store configs
        return {
            "model": "gpt-4o",
            "mode": "enhanced",
            "embedding_model": "text-embedding-ada-002",

            # Metadata store configuration (for storing metadata documents)
            "meta_store": {
                "type": "memory",  # memory, postgres, redis
                "connection_string": os.environ.get("RYOMA_META_STORE_CONNECTION"),
                "options": {}
            },

            # Vector store configuration (for vector indexing/searching)
            "vector_store": {
                "type": "pgvector",  # chroma, faiss, qdrant, milvus, pgvector
                "collection_name": "ryoma_vectors",
                "dimension": 768,
                "distance_metric": "cosine",
                "extra_configs": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "postgres",
                    "user": os.environ.get("POSTGRES_USER", ""),
                    "password": os.environ.get("POSTGRES_PASSWORD", ""),
                    "distance_strategy": "cosine"
                }
            },

            # Data source configuration (for connecting to databases)
            "datasources": [
                {
                    "name": "default",
                    "type": "postgres",
                    "host": "localhost",
                    "port": 5432,
                    "database": "postgres",
                    "user": os.environ.get("POSTGRES_USER", ""),
                    "password": os.environ.get("POSTGRES_PASSWORD", ""),
                }
            ],

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

    def get_meta_store_config(self) -> StoreConfig:
        """
        Get metadata store configuration as StoreConfig object.

        Returns:
            StoreConfig: Configuration for metadata storage
        """
        meta_config = self.get_config("meta_store", {})
        return StoreConfig(
            type=meta_config.get("type", "memory"),
            connection_string=meta_config.get("connection_string"),
            options=meta_config.get("options", {})
        )

    def get_vector_store_config(self) -> VectorStoreConfig:
        """
        Get vector store configuration as VectorStoreConfig object.

        Returns:
            VectorStoreConfig: Configuration for vector storage
        """
        vector_config = self.get_config("vector_store", {})
        return VectorStoreConfig(
            type=vector_config.get("type", "pgvector"),
            collection_name=vector_config.get("collection_name", "ryoma_vectors"),
            dimension=vector_config.get("dimension", 768),
            distance_metric=vector_config.get("distance_metric", "cosine"),
            extra_configs=vector_config.get("extra_configs", {})
        )

    def get_datasources_list(self) -> list[Dict[str, Any]]:
        """
        Get all datasource configurations as a list.

        Returns:
            List of datasource configurations
        """
        return self.get_config("datasources", [])

    def get_datasource_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific datasource configuration by name.

        Args:
            name: Name of the datasource

        Returns:
            Dict with datasource config or None if not found
        """
        datasources = self.get_datasources_list()
        for ds in datasources:
            if ds.get("name") == name:
                return ds
        return None

    def get_default_datasource_config(self) -> Optional[Dict[str, Any]]:
        """
        Get the default (first) datasource configuration.

        Returns:
            Dict with datasource config or None if not configured
        """
        datasources = self.get_datasources_list()
        if datasources:
            # Return the first datasource or one explicitly named 'default'
            default_ds = self.get_datasource_by_name("default")
            return default_ds if default_ds else datasources[0]
        return None

    def add_datasource_config(self, config: Dict[str, Any]) -> None:
        """
        Add a new datasource configuration.

        Args:
            config: Datasource configuration dictionary (must include 'name' field)
        """
        if "name" not in config:
            raise ValueError("Datasource configuration must include 'name' field")

        datasources = self.get_datasources_list()

        # Check if datasource with same name already exists
        for i, ds in enumerate(datasources):
            if ds.get("name") == config["name"]:
                # Update existing datasource
                datasources[i] = config
                self.update_config("datasources", datasources)
                return

        # Add new datasource
        datasources.append(config)
        self.update_config("datasources", datasources)

    def remove_datasource_config(self, name: str) -> None:
        """
        Remove a datasource configuration by name.

        Args:
            name: Name of the datasource configuration to remove
        """
        datasources = self.get_datasources_list()
        datasources = [ds for ds in datasources if ds.get("name") != name]
        self.update_config("datasources", datasources)
