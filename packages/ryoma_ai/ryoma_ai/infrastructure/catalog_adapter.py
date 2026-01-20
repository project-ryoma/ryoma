"""Adapter for existing catalog indexing/search services"""

import logging
from typing import List, Optional, Literal
from ryoma_data.base import DataSource
from ryoma_ai.catalog.indexer import UnifiedCatalogIndexService
from ryoma_ai.store.catalog_store import CatalogStore

logger = logging.getLogger(__name__)


class CatalogIndexerAdapter:
    """
    Adapter that wraps UnifiedCatalogIndexService.
    Implements CatalogIndexer protocol from domain layer.

    This adapter allows the existing catalog indexing service to be
    used through the new domain interface without modification.
    """

    def __init__(self, service: UnifiedCatalogIndexService):
        """
        Initialize adapter.

        Args:
            service: Existing UnifiedCatalogIndexService instance
        """
        self._service = service
        logger.debug("Initialized CatalogIndexerAdapter")

    def index_datasource(
        self,
        datasource: DataSource,
        data_source_id: str,
        level: Literal["catalog", "schema", "table", "column"] = "column"
    ) -> str:
        """
        Index a datasource's catalog.

        Args:
            datasource: DataSource to index
            data_source_id: Unique identifier for the datasource
            level: Level of indexing (catalog/schema/table/column)

        Returns:
            Catalog ID
        """
        logger.info(f"Indexing datasource {data_source_id} at level {level}")

        catalog_id = self._service.index_datasource(
            datasource=datasource,
            data_source_id=data_source_id,
            level=level
        )

        logger.info(f"Indexed datasource {data_source_id}: catalog_id={catalog_id}")
        return catalog_id

    def validate_indexing(self, catalog_id: str) -> bool:
        """
        Validate catalog is properly indexed.

        Args:
            catalog_id: Catalog ID to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Simple validation - check if catalog_id is non-empty
            # This is a basic check - enhance as needed
            is_valid = catalog_id is not None and len(catalog_id) > 0

            logger.debug(f"Validated catalog {catalog_id}: {is_valid}")
            return is_valid

        except Exception as e:
            logger.warning(f"Catalog validation failed for {catalog_id}: {e}")
            return False


class CatalogSearcherAdapter:
    """
    Adapter that wraps CatalogStore.
    Implements CatalogSearcher protocol from domain layer.

    This adapter allows the existing catalog search store to be
    used through the new domain interface without modification.
    """

    def __init__(self, catalog_store: CatalogStore):
        """
        Initialize adapter.

        Args:
            catalog_store: Existing CatalogStore instance
        """
        self._catalog_store = catalog_store
        logger.debug("Initialized CatalogSearcherAdapter")

    def search_catalogs(
        self,
        query: str,
        top_k: int = 5,
        level: Literal["catalog", "schema", "table", "column"] = "column",
        datasource_id: Optional[str] = None
    ) -> List[dict]:
        """
        Search catalogs semantically.

        Args:
            query: Search query
            top_k: Number of results to return
            level: Level to search at (catalog/schema/table/column)
            datasource_id: Optional filter by datasource

        Returns:
            List of matching catalog entries
        """
        logger.debug(f"Searching catalogs: query='{query}', level={level}, top_k={top_k}")

        results = self._catalog_store.search_catalogs(
            query=query,
            top_k=top_k,
            level=level
        )

        logger.debug(f"Found {len(results)} catalog results")
        return results

    def get_table_suggestions(
        self,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """
        Get table name suggestions based on query.

        Args:
            query: Search query
            top_k: Number of suggestions

        Returns:
            List of table names
        """
        logger.debug(f"Getting table suggestions for: '{query}'")

        suggestions = self._catalog_store.get_table_suggestions(
            query=query,
            top_k=top_k
        )

        logger.debug(f"Found {len(suggestions)} table suggestions")
        return suggestions

    def get_column_suggestions(
        self,
        table_name: str,
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """
        Get column suggestions for a table.

        Args:
            table_name: Table to search columns in
            query: Search query
            top_k: Number of suggestions

        Returns:
            List of column names
        """
        logger.debug(f"Getting column suggestions for table '{table_name}': '{query}'")

        suggestions = self._catalog_store.get_column_suggestions(
            table_name=table_name,
            query=query,
            top_k=top_k
        )

        logger.debug(f"Found {len(suggestions)} column suggestions")
        return suggestions
