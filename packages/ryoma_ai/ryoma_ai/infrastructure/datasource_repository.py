"""Repository implementation for datasource persistence"""

import logging
from typing import List
from langchain_core.stores import BaseStore
from ryoma_data.base import DataSource
from ryoma_ai.domain.constants import StoreKeys

logger = logging.getLogger(__name__)


class StoreBasedDataSourceRepository:
    """
    DataSource repository using LangChain BaseStore.
    Implements DataSourceRepository protocol from domain layer.

    This repository provides persistence for datasources using any
    LangChain BaseStore implementation (InMemory, Postgres, Redis, etc.)
    """

    def __init__(self, store: BaseStore):
        """
        Initialize repository.

        Args:
            store: LangChain BaseStore for persistence
        """
        self._store = store
        logger.debug("Initialized StoreBasedDataSourceRepository")

    def save(self, datasource: DataSource) -> None:
        """
        Save a datasource to the store.

        Args:
            datasource: DataSource to save
        """
        # Save datasource with its ID as key
        key = f"{StoreKeys.DATASOURCES_PREFIX}{datasource.id}"
        self._store.mset([(key, datasource)])

        # Update list of datasource IDs
        self._add_to_datasource_list(datasource.id)

        logger.info(f"Saved datasource: {datasource.id}")

    def get_active(self) -> DataSource:
        """
        Get the currently active datasource.

        Returns:
            The active datasource

        Raises:
            ValueError: If no active datasource is configured
        """
        # Try new key first (multi-datasource support)
        results = self._store.mget([StoreKeys.ACTIVE_DATASOURCE_ID])
        active_id = results[0] if results and results[0] else None

        if active_id:
            logger.debug(f"Found active datasource ID: {active_id}")
            return self.get_by_id(active_id)

        # Fall back to old key for backward compatibility
        results = self._store.mget([StoreKeys.ACTIVE_DATASOURCE])
        datasource = results[0] if results and results[0] else None

        if not datasource:
            raise ValueError(
                "No active datasource configured. "
                "Use add_datasource() or set_active_datasource() first."
            )

        logger.debug(f"Found active datasource (legacy key): {datasource.id}")
        return datasource

    def set_active(self, datasource_id: str) -> None:
        """
        Set which datasource is active.

        Args:
            datasource_id: ID of datasource to make active

        Raises:
            ValueError: If datasource not found
        """
        # Verify datasource exists
        datasource = self.get_by_id(datasource_id)

        # Set new key for multi-datasource support
        self._store.mset(
            [
                (StoreKeys.ACTIVE_DATASOURCE_ID, datasource_id),
                (StoreKeys.ACTIVE_DATASOURCE, datasource),  # Backward compat
            ]
        )

        logger.info(f"Set active datasource: {datasource_id}")

    def get_by_id(self, datasource_id: str) -> DataSource:
        """
        Get datasource by ID.

        Args:
            datasource_id: ID of datasource to retrieve

        Returns:
            The requested datasource

        Raises:
            ValueError: If datasource not found
        """
        key = f"{StoreKeys.DATASOURCES_PREFIX}{datasource_id}"
        results = self._store.mget([key])
        datasource = results[0] if results and results[0] else None

        if not datasource:
            raise ValueError(f"Datasource not found: {datasource_id}")

        logger.debug(f"Retrieved datasource: {datasource_id}")
        return datasource

    def list_all(self) -> List[DataSource]:
        """
        List all registered datasources.

        Returns:
            List of all datasources
        """
        # Get list of datasource IDs
        results = self._store.mget([StoreKeys.DATASOURCE_IDS])
        datasource_ids = results[0] if results and results[0] else []

        datasources = []
        for ds_id in datasource_ids:
            try:
                datasources.append(self.get_by_id(ds_id))
            except ValueError:
                logger.warning(f"Datasource {ds_id} not found in store")

        logger.debug(f"Listed {len(datasources)} datasources")
        return datasources

    def delete(self, datasource_id: str) -> None:
        """
        Delete a datasource.

        Args:
            datasource_id: ID of datasource to delete

        Raises:
            ValueError: If datasource not found
        """
        # Verify exists first
        self.get_by_id(datasource_id)

        # Delete from store
        # Note: BaseStore doesn't have delete, so we set to None
        # This is a limitation of the current store interface
        key = f"{StoreKeys.DATASOURCES_PREFIX}{datasource_id}"
        self._store.mset([(key, None)])

        # Remove from datasource_ids list
        self._remove_from_datasource_list(datasource_id)

        logger.info(f"Deleted datasource: {datasource_id}")

    def _add_to_datasource_list(self, datasource_id: str) -> None:
        """Add datasource ID to the list of all datasources"""
        results = self._store.mget([StoreKeys.DATASOURCE_IDS])
        datasource_ids = results[0] if results and results[0] else []

        if datasource_id not in datasource_ids:
            datasource_ids.append(datasource_id)
            self._store.mset([(StoreKeys.DATASOURCE_IDS, datasource_ids)])

    def _remove_from_datasource_list(self, datasource_id: str) -> None:
        """Remove datasource ID from the list of all datasources"""
        results = self._store.mget([StoreKeys.DATASOURCE_IDS])
        datasource_ids = results[0] if results and results[0] else []

        if datasource_id in datasource_ids:
            datasource_ids.remove(datasource_id)
            self._store.mset([(StoreKeys.DATASOURCE_IDS, datasource_ids)])
