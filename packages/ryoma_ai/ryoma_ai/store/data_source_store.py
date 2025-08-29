"""
Data source store using LangChain BaseStore for persistence and management.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from langchain_core.stores import BaseStore
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.store.store_factory import StoreFactory
from ryoma_ai.datasource.factory import DataSourceFactory
from ryoma_ai.models.datasource import DataSourceRegistration
from ryoma_ai.store.exceptions import (
    DataSourceConnectionError,
    DataSourceNotFoundError,
    StoreException,
)

logger = logging.getLogger(__name__)


class DataSourceStore:
    """
    Store for managing multiple data sources using LangChain BaseStore.

    Provides registration, retrieval, and lifecycle management of data sources
    with persistent storage and caching capabilities.
    """

    def __init__(self, store: BaseStore[str, str]):
        """
        Initialize the data source store.

        Args:
            store: LangChain BaseStore implementation (required to avoid duplication)
        """
        if not store:
            raise ValueError("store is required - pass store from CLI to avoid duplication")
        self.store = store
        self._datasource_cache: Dict[str, DataSource] = {}
        self._registration_cache: Dict[str, DataSourceRegistration] = {}
        self._key_prefix = "datasource:"

        # Load existing registrations from store
        self._load_registrations()

    def _load_registrations(self) -> None:
        """Load all existing data source registrations from store."""
        try:
            # Get all keys with our prefix
            all_keys = []
            try:
                # Some stores support listing keys, others don't
                if hasattr(self.store, "yield_keys"):
                    all_keys = list(self.store.yield_keys())
                elif hasattr(self.store, "keys"):
                    all_keys = list(self.store.keys())
            except Exception:
                # Store doesn't support key listing, we'll populate cache as needed
                pass

            datasource_keys = [
                key for key in all_keys if key.startswith(self._key_prefix)
            ]

            for key in datasource_keys:
                try:
                    data = self.store.mget([key])[0]
                    if data:
                        reg_dict = json.loads(data)
                        registration = DataSourceRegistration.from_dict(reg_dict)
                        ds_id = key.replace(self._key_prefix, "")
                        self._registration_cache[ds_id] = registration
                        logger.debug(f"Loaded data source registration: {ds_id}")
                except Exception as e:
                    logger.warning(f"Failed to load data source from key {key}: {e}")
        except Exception as e:
            logger.warning(f"Failed to load data source registrations: {e}")

    def register_data_source(
        self,
        name: str,
        datasource_type: str,
        config: Dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        data_source_id: Optional[str] = None,
    ) -> str:
        """
        Register a new data source in the store.

        Args:
            name: Human-readable name for the data source
            datasource_type: Type of data source (postgres, mysql, etc.)
            config: Configuration dictionary for the data source
            description: Optional description
            tags: Optional list of tags
            data_source_id: Optional custom ID, will generate UUID if not provided

        Returns:
            str: The data source ID

        Raises:
            StoreException: If registration fails
            DataSourceConnectionError: If data source connection test fails
        """
        if not data_source_id:
            data_source_id = str(uuid4())

        # Test connection before registering
        try:
            test_datasource = DataSourceFactory.create_datasource(
                datasource_type, **config
            )
            # Simple connection test
            test_datasource.get_catalog()
            logger.info(f"Connection test successful for data source: {name}")
        except Exception as e:
            raise DataSourceConnectionError(
                data_source_id, f"Connection test failed: {str(e)}", e
            )

        # Create registration
        registration = DataSourceRegistration(
            id=data_source_id,
            name=name,
            type=datasource_type,
            config=config,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
            description=description,
            tags=tags or [],
        )

        # Store in persistent store
        try:
            key = f"{self._key_prefix}{data_source_id}"
            data = json.dumps(registration.to_dict())
            self.store.mset([(key, data)])

            # Update cache
            self._registration_cache[data_source_id] = registration

            logger.info(f"Registered data source: {name} ({data_source_id})")
            return data_source_id

        except Exception as e:
            raise StoreException(f"Failed to register data source '{name}'", e)

    def get_data_source(self, data_source_id: str) -> DataSource:
        """
        Get a data source instance by ID.

        Args:
            data_source_id: The data source ID

        Returns:
            DataSource: The data source instance

        Raises:
            DataSourceNotFoundError: If data source is not found
        """
        # Check cache first
        if data_source_id in self._datasource_cache:
            return self._datasource_cache[data_source_id]

        # Get registration
        registration = self.get_registration(data_source_id)

        # Create data source instance
        try:
            datasource = DataSourceFactory.create_datasource(
                registration.type, **registration.config
            )

            # Cache the instance
            self._datasource_cache[data_source_id] = datasource
            return datasource

        except Exception as e:
            raise DataSourceConnectionError(
                data_source_id, f"Failed to create data source instance: {str(e)}", e
            )

    def get_registration(self, data_source_id: str) -> DataSourceRegistration:
        """
        Get data source registration information.

        Args:
            data_source_id: The data source ID

        Returns:
            DataSourceRegistration: The registration information

        Raises:
            DataSourceNotFoundError: If data source is not found
        """
        # Check cache first
        if data_source_id in self._registration_cache:
            return self._registration_cache[data_source_id]

        # Try to load from store
        try:
            key = f"{self._key_prefix}{data_source_id}"
            data = self.store.mget([key])[0]
            if not data:
                raise DataSourceNotFoundError(data_source_id)

            reg_dict = json.loads(data)
            registration = DataSourceRegistration.from_dict(reg_dict)

            # Cache it
            self._registration_cache[data_source_id] = registration
            return registration

        except DataSourceNotFoundError:
            raise
        except Exception as e:
            raise DataSourceNotFoundError(data_source_id, e)

    def list_data_sources(
        self,
        active_only: bool = True,
        datasource_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[DataSourceRegistration]:
        """
        List all registered data sources.

        Args:
            active_only: Only return active data sources
            datasource_type: Filter by data source type
            tags: Filter by tags (must have all specified tags)

        Returns:
            List[DataSourceRegistration]: List of registrations
        """
        registrations = list(self._registration_cache.values())

        # Apply filters
        if active_only:
            registrations = [r for r in registrations if r.is_active]

        if datasource_type:
            registrations = [r for r in registrations if r.type == datasource_type]

        if tags:
            registrations = [
                r
                for r in registrations
                if r.tags and all(tag in r.tags for tag in tags)
            ]

        return registrations

    def update_data_source(
        self,
        data_source_id: str,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
    ) -> None:
        """
        Update data source registration.

        Args:
            data_source_id: The data source ID
            name: New name (optional)
            config: New configuration (optional)
            description: New description (optional)
            tags: New tags (optional)
            is_active: New active status (optional)

        Raises:
            DataSourceNotFoundError: If data source is not found
            DataSourceConnectionError: If new config fails connection test
            StoreException: If update fails
        """
        registration = self.get_registration(data_source_id)

        # Test new config if provided
        if config:
            try:
                test_datasource = DataSourceFactory.create_datasource(
                    registration.type, **config
                )
                test_datasource.get_catalog()
            except Exception as e:
                raise DataSourceConnectionError(
                    data_source_id, f"New configuration test failed: {str(e)}", e
                )

        # Update fields
        if name is not None:
            registration.name = name
        if config is not None:
            registration.config = config
        if description is not None:
            registration.description = description
        if tags is not None:
            registration.tags = tags
        if is_active is not None:
            registration.is_active = is_active

        registration.updated_at = datetime.now()

        # Save to store
        try:
            key = f"{self._key_prefix}{data_source_id}"
            data = json.dumps(registration.to_dict())
            self.store.mset([(key, data)])

            # Update cache
            self._registration_cache[data_source_id] = registration

            # Clear datasource cache to force recreation
            if data_source_id in self._datasource_cache:
                del self._datasource_cache[data_source_id]

            logger.info(f"Updated data source: {data_source_id}")

        except Exception as e:
            raise StoreException(f"Failed to update data source '{data_source_id}'", e)

    def remove_data_source(self, data_source_id: str) -> None:
        """
        Remove a data source from the store.

        Args:
            data_source_id: The data source ID

        Raises:
            DataSourceNotFoundError: If data source is not found
            StoreException: If removal fails
        """
        # Check if exists
        self.get_registration(data_source_id)

        try:
            # Remove from store
            key = f"{self._key_prefix}{data_source_id}"
            self.store.mdelete([key])

            # Remove from caches
            self._registration_cache.pop(data_source_id, None)
            self._datasource_cache.pop(data_source_id, None)

            logger.info(f"Removed data source: {data_source_id}")

        except Exception as e:
            raise StoreException(f"Failed to remove data source '{data_source_id}'", e)

    def test_connection(self, data_source_id: str) -> bool:
        """
        Test connection to a data source.

        Args:
            data_source_id: The data source ID

        Returns:
            bool: True if connection successful

        Raises:
            DataSourceNotFoundError: If data source is not found
        """
        try:
            datasource = self.get_data_source(data_source_id)
            datasource.get_catalog()
            return True
        except DataSourceNotFoundError:
            raise
        except Exception as e:
            logger.warning(f"Connection test failed for {data_source_id}: {e}")
            return False

    def clear_cache(self) -> None:
        """Clear all cached data source instances."""
        self._datasource_cache.clear()
        logger.info("Cleared data source cache")
