"""Service for datasource management"""

import logging
from typing import List
from ryoma_data.base import DataSource
from ryoma_ai.domain.interfaces import DataSourceRepository

logger = logging.getLogger(__name__)


class DataSourceService:
    """
    Service for managing datasources.

    This service encapsulates all datasource-related operations,
    providing a clean API for adding, retrieving, and managing
    datasources without exposing persistence details.
    """

    def __init__(self, repository: DataSourceRepository):
        """
        Initialize service.

        Args:
            repository: Repository for datasource persistence
        """
        self._repository = repository
        logger.debug("Initialized DataSourceService")

    def add_datasource(self, datasource: DataSource) -> None:
        """
        Add a new datasource.

        This will save the datasource and automatically set it as
        the active datasource.

        Args:
            datasource: DataSource to add

        Example:
            >>> from ryoma_data.sql import DataSource
            >>> ds = DataSource(backend="duckdb", database=":memory:")
            >>> service.add_datasource(ds)
        """
        self._repository.save(datasource)
        self._repository.set_active(datasource.id)
        logger.info(f"Added and activated datasource: {datasource.id}")

    def get_active_datasource(self) -> DataSource:
        """
        Get the currently active datasource.

        Returns:
            The active datasource

        Raises:
            ValueError: If no active datasource is configured

        Example:
            >>> ds = service.get_active_datasource()
            >>> print(ds.id)
        """
        return self._repository.get_active()

    def set_active_datasource(self, datasource_id: str) -> None:
        """
        Set which datasource is active.

        Args:
            datasource_id: ID of datasource to make active

        Raises:
            ValueError: If datasource not found

        Example:
            >>> service.set_active_datasource("my_postgres_db")
        """
        self._repository.set_active(datasource_id)
        logger.info(f"Activated datasource: {datasource_id}")

    def get_datasource(self, datasource_id: str) -> DataSource:
        """
        Get a datasource by ID.

        Args:
            datasource_id: ID of datasource to retrieve

        Returns:
            The requested datasource

        Raises:
            ValueError: If datasource not found

        Example:
            >>> ds = service.get_datasource("my_postgres_db")
        """
        return self._repository.get_by_id(datasource_id)

    def list_datasources(self) -> List[DataSource]:
        """
        List all registered datasources.

        Returns:
            List of all datasources

        Example:
            >>> datasources = service.list_datasources()
            >>> for ds in datasources:
            ...     print(f"{ds.id}: {ds.backend}")
        """
        datasources = self._repository.list_all()
        logger.debug(f"Listed {len(datasources)} datasources")
        return datasources

    def remove_datasource(self, datasource_id: str) -> None:
        """
        Remove a datasource.

        Warning: This will delete the datasource permanently.
        If this is the active datasource, you'll need to set
        a new active datasource afterward.

        Args:
            datasource_id: ID of datasource to remove

        Raises:
            ValueError: If datasource not found

        Example:
            >>> service.remove_datasource("old_db")
        """
        self._repository.delete(datasource_id)
        logger.info(f"Removed datasource: {datasource_id}")

    def has_active_datasource(self) -> bool:
        """
        Check if there is an active datasource configured.

        Returns:
            True if active datasource exists, False otherwise

        Example:
            >>> if service.has_active_datasource():
            ...     ds = service.get_active_datasource()
        """
        try:
            self._repository.get_active()
            return True
        except ValueError:
            return False
