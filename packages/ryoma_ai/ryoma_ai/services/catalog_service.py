"""Service for catalog indexing and search operations"""

import logging
from typing import List, Optional, Literal
from ryoma_data.base import DataSource
from ryoma_ai.domain.interfaces import CatalogIndexer, CatalogSearcher
from ryoma_ai.domain.constants import AgentDefaults

logger = logging.getLogger(__name__)


class CatalogService:
    """
    Service for catalog indexing and search.

    This service encapsulates all catalog-related operations, providing
    a clean API for indexing datasource metadata and searching it
    semantically.
    """

    def __init__(
        self,
        indexer: CatalogIndexer,
        searcher: CatalogSearcher,
    ):
        """
        Initialize service.

        Args:
            indexer: Catalog indexing implementation
            searcher: Catalog search implementation
        """
        self._indexer = indexer
        self._searcher = searcher
        logger.debug("Initialized CatalogService")

    # === Indexing Operations ===

    def index_datasource(
        self,
        datasource: DataSource,
        level: Literal["catalog", "schema", "table", "column"] = "column"
    ) -> str:
        """
        Index a datasource's catalog.

        This creates a semantic index of the datasource's metadata
        (tables, columns, descriptions, etc.) for later search.

        Args:
            datasource: DataSource to index
            level: Level of indexing (catalog/schema/table/column)
                - catalog: Index only catalog-level metadata
                - schema: Index catalog and schema metadata
                - table: Index up to table-level metadata
                - column: Index everything including columns (default)

        Returns:
            Catalog ID - unique identifier for the indexed catalog

        Example:
            >>> catalog_id = service.index_datasource(
            ...     datasource=my_db,
            ...     level="column"
            ... )
            >>> print(f"Indexed with ID: {catalog_id}")
        """
        catalog_id = self._indexer.index_datasource(
            datasource=datasource,
            data_source_id=datasource.id,
            level=level
        )

        logger.info(
            f"Indexed datasource {datasource.id} at level {level}: {catalog_id}"
        )
        return catalog_id

    def index_multiple_datasources(
        self,
        datasources: List[DataSource],
        level: Literal["catalog", "schema", "table", "column"] = "column"
    ) -> List[str]:
        """
        Index multiple datasources.

        This is a convenience method for indexing multiple datasources
        at once. Failed indexing attempts are logged but don't stop
        the process.

        Args:
            datasources: List of datasources to index
            level: Level of indexing

        Returns:
            List of catalog IDs for successfully indexed datasources

        Example:
            >>> catalog_ids = service.index_multiple_datasources(
            ...     datasources=[db1, db2, db3],
            ...     level="table"
            ... )
            >>> print(f"Indexed {len(catalog_ids)} datasources")
        """
        catalog_ids = []

        for datasource in datasources:
            try:
                catalog_id = self.index_datasource(datasource, level)
                catalog_ids.append(catalog_id)
            except Exception as e:
                logger.error(f"Failed to index {datasource.id}: {e}")

        logger.info(
            f"Successfully indexed {len(catalog_ids)}/{len(datasources)} datasources"
        )
        return catalog_ids

    def validate_indexing(self, catalog_id: str) -> bool:
        """
        Validate that a catalog is properly indexed.

        Args:
            catalog_id: Catalog ID to validate

        Returns:
            True if valid, False otherwise

        Example:
            >>> if service.validate_indexing(catalog_id):
            ...     print("Catalog is valid")
        """
        is_valid = self._indexer.validate_indexing(catalog_id)
        logger.debug(f"Validated catalog {catalog_id}: {is_valid}")
        return is_valid

    # === Search Operations ===

    def search_tables(
        self,
        query: str,
        top_k: int = AgentDefaults.DEFAULT_TOP_K,
        datasource_id: Optional[str] = None
    ) -> List[dict]:
        """
        Search for relevant tables based on a natural language query.

        Args:
            query: Natural language search query
                (e.g., "customer purchase history")
            top_k: Number of results to return
            datasource_id: Optional filter by datasource

        Returns:
            List of table metadata dictionaries, each containing:
                - table_name: Name of the table
                - schema: Schema name (if applicable)
                - description: Table description
                - score: Relevance score

        Example:
            >>> tables = service.search_tables(
            ...     query="customer transactions",
            ...     top_k=3
            ... )
            >>> for table in tables:
            ...     print(f"{table['table_name']}: {table['description']}")
        """
        logger.debug(f"Searching tables: query='{query}', top_k={top_k}")

        results = self._searcher.search_catalogs(
            query=query,
            top_k=top_k,
            level="table",
            datasource_id=datasource_id
        )

        logger.debug(f"Found {len(results)} table results")
        return results

    def search_columns(
        self,
        query: str,
        table_name: Optional[str] = None,
        top_k: int = AgentDefaults.DEFAULT_TOP_K
    ) -> List[dict]:
        """
        Search for relevant columns based on a natural language query.

        Args:
            query: Natural language search query
                (e.g., "email address")
            table_name: Optional filter by table name
            top_k: Number of results to return

        Returns:
            List of column metadata dictionaries, each containing:
                - column_name: Name of the column
                - table_name: Table containing the column
                - data_type: Column data type
                - description: Column description
                - score: Relevance score

        Example:
            >>> columns = service.search_columns(
            ...     query="customer email",
            ...     table_name="customers"
            ... )
            >>> for col in columns:
            ...     print(f"{col['column_name']}: {col['data_type']}")
        """
        logger.debug(
            f"Searching columns: query='{query}', table='{table_name}', top_k={top_k}"
        )

        if table_name:
            results = self._searcher.get_column_suggestions(
                table_name=table_name,
                query=query,
                top_k=top_k
            )
            # Convert to consistent format
            results = [{"column_name": col} for col in results]
        else:
            results = self._searcher.search_catalogs(
                query=query,
                top_k=top_k,
                level="column"
            )

        logger.debug(f"Found {len(results)} column results")
        return results

    def get_table_suggestions(
        self,
        query: str,
        top_k: int = AgentDefaults.DEFAULT_TOP_K
    ) -> List[str]:
        """
        Get table name suggestions based on query.

        This is a simplified version of search_tables that returns
        just the table names, useful for autocomplete and suggestions.

        Args:
            query: Search query
            top_k: Number of suggestions

        Returns:
            List of table names

        Example:
            >>> suggestions = service.get_table_suggestions("customer")
            >>> print(suggestions)
            ['customers', 'customer_orders', 'customer_reviews']
        """
        logger.debug(f"Getting table suggestions for: '{query}'")

        suggestions = self._searcher.get_table_suggestions(query, top_k)

        logger.debug(f"Found {len(suggestions)} table suggestions")
        return suggestions

    def get_column_suggestions(
        self,
        table_name: str,
        query: str,
        top_k: int = AgentDefaults.DEFAULT_TOP_K
    ) -> List[str]:
        """
        Get column suggestions for a specific table.

        This is useful for autocomplete when writing queries or
        exploring table structure.

        Args:
            table_name: Table to search columns in
            query: Search query
            top_k: Number of suggestions

        Returns:
            List of column names

        Example:
            >>> suggestions = service.get_column_suggestions(
            ...     table_name="customers",
            ...     query="email"
            ... )
            >>> print(suggestions)
            ['email', 'email_verified', 'secondary_email']
        """
        logger.debug(
            f"Getting column suggestions for table '{table_name}': '{query}'"
        )

        suggestions = self._searcher.get_column_suggestions(
            table_name=table_name,
            query=query,
            top_k=top_k
        )

        logger.debug(f"Found {len(suggestions)} column suggestions")
        return suggestions
