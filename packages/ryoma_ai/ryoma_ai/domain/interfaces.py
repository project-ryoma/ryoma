"""Domain interfaces - protocols for dependency inversion"""

from typing import Protocol, List, Optional, Literal
from ryoma_data.base import DataSource


class DataSourceRepository(Protocol):
    """
    Repository for managing datasources.

    This protocol defines the interface for datasource persistence,
    allowing different storage implementations (in-memory, database, etc.)
    without coupling domain logic to storage details.
    """

    def save(self, datasource: DataSource) -> None:
        """
        Save a datasource to the repository.

        Args:
            datasource: DataSource instance to save
        """
        ...

    def get_active(self) -> DataSource:
        """
        Get the currently active datasource.

        Returns:
            The active DataSource

        Raises:
            ValueError: If no active datasource is configured
        """
        ...

    def set_active(self, datasource_id: str) -> None:
        """
        Set which datasource is active.

        Args:
            datasource_id: ID of datasource to make active

        Raises:
            ValueError: If datasource with given ID not found
        """
        ...

    def get_by_id(self, datasource_id: str) -> DataSource:
        """
        Get a datasource by its ID.

        Args:
            datasource_id: ID of datasource to retrieve

        Returns:
            The requested DataSource

        Raises:
            ValueError: If datasource not found
        """
        ...

    def list_all(self) -> List[DataSource]:
        """
        List all registered datasources.

        Returns:
            List of all datasources in the repository
        """
        ...

    def delete(self, datasource_id: str) -> None:
        """
        Delete a datasource from the repository.

        Args:
            datasource_id: ID of datasource to delete

        Raises:
            ValueError: If datasource not found
        """
        ...


class CatalogIndexer(Protocol):
    """
    Protocol for catalog indexing operations.

    This protocol defines the interface for indexing datasource catalogs
    (metadata about tables, columns, etc.) for semantic search.
    """

    def index_datasource(
        self,
        datasource: DataSource,
        data_source_id: str,
        level: Literal["catalog", "schema", "table", "column"] = "column",
    ) -> str:
        """
        Index a datasource's catalog metadata.

        Args:
            datasource: DataSource to index
            data_source_id: Unique identifier for the datasource
            level: Level of indexing (catalog/schema/table/column)

        Returns:
            Catalog ID - unique identifier for the indexed catalog

        Raises:
            ValueError: If datasource cannot be indexed
        """
        ...

    def validate_indexing(self, catalog_id: str) -> bool:
        """
        Validate that a catalog is properly indexed.

        Args:
            catalog_id: Catalog ID to validate

        Returns:
            True if catalog is valid and properly indexed, False otherwise
        """
        ...


class CatalogSearcher(Protocol):
    """
    Protocol for catalog search operations.

    This protocol defines the interface for searching indexed catalog
    metadata using semantic search.
    """

    def search_catalogs(
        self,
        query: str,
        top_k: int = 5,
        level: Literal["catalog", "schema", "table", "column"] = "column",
        datasource_id: Optional[str] = None,
    ) -> List[dict]:
        """
        Search catalogs semantically.

        Args:
            query: Search query string
            top_k: Number of results to return
            level: Level to search at (catalog/schema/table/column)
            datasource_id: Optional filter by datasource ID

        Returns:
            List of matching catalog entries as dictionaries
        """
        ...

    def get_table_suggestions(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[str]:
        """
        Get table name suggestions based on query.

        Args:
            query: Search query string
            top_k: Number of suggestions to return

        Returns:
            List of suggested table names
        """
        ...

    def get_column_suggestions(
        self,
        table_name: str,
        query: str,
        top_k: int = 5,
    ) -> List[str]:
        """
        Get column suggestions for a specific table.

        Args:
            table_name: Name of the table to search columns in
            query: Search query string
            top_k: Number of suggestions to return

        Returns:
            List of suggested column names
        """
        ...
