"""
Catalog store using LangChain stores and vector stores for indexing and search.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from langchain_core.embeddings import Embeddings
from langchain_core.stores import BaseStore
from langchain_core.vectorstores import VectorStore
from ryoma_ai.catalog import UnifiedCatalogIndexService
from ryoma_ai.catalog.exceptions import CatalogIndexError
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.metadata import Catalog, Column, Schema, Table
from ryoma_ai.models.catalog import CatalogIndex
from ryoma_ai.store.exceptions import CatalogNotFoundError, StoreException


class CatalogNotIndexedError(Exception):
    """Raised when catalog search is attempted without proper indexing."""

    pass


logger = logging.getLogger(__name__)


class CatalogStore:
    """
    Store for managing and indexing data source catalogs using LangChain stores.

    Provides catalog indexing, search, and metadata management with both
    structured storage and vector-based semantic search capabilities.
    """

    def __init__(
        self,
        metadata_store: BaseStore[str, str],
        vector_store: Optional[VectorStore] = None,
        embedding_function: Optional[Embeddings] = None,
    ):
        """
        Initialize the catalog store.

        Args:
            metadata_store: LangChain BaseStore for catalog metadata (required)
            vector_store: LangChain VectorStore for semantic search
            embedding_function: Embeddings for vector indexing
        """
        if not metadata_store:
            raise ValueError(
                "metadata_store is required - pass store from CLI to avoid duplication"
            )
        self.metadata_store = metadata_store
        self.vector_store = vector_store
        self.embedding_function = embedding_function

        self._catalog_cache: Dict[str, Catalog] = {}
        self._index_cache: Dict[str, CatalogIndex] = {}
        self._metadata_prefix = "catalog_meta:"
        self._catalog_prefix = "catalog_data:"

        # Initialize unified indexing service
        self._index_service = UnifiedCatalogIndexService(
            vector_store=self.vector_store,
            metadata_store=self.metadata_store,
        )

        # Load existing indexes
        self._load_indexes()

    def _load_indexes(self) -> None:
        """Load existing catalog indexes from metadata store."""
        try:
            all_keys = []
            try:
                if hasattr(self.metadata_store, "yield_keys"):
                    all_keys = list(self.metadata_store.yield_keys())
                elif hasattr(self.metadata_store, "keys"):
                    all_keys = list(self.metadata_store.keys())
            except Exception:
                pass

            index_keys = [
                key for key in all_keys if key.startswith(self._metadata_prefix)
            ]

            for key in index_keys:
                try:
                    data = self.metadata_store.mget([key])[0]
                    if data:
                        index_dict = json.loads(data)
                        index = CatalogIndex.from_dict(index_dict)
                        catalog_id = key.replace(self._metadata_prefix, "")
                        self._index_cache[catalog_id] = index
                        logger.debug(f"Loaded catalog index: {catalog_id}")
                except Exception as e:
                    logger.warning(f"Failed to load catalog index from key {key}: {e}")
        except Exception as e:
            logger.warning(f"Failed to load catalog indexes: {e}")

    def index_catalog(
        self,
        data_source_id: str,
        datasource: DataSource,
        index_level: str = "table",
        catalog_id: Optional[str] = None,
    ) -> str:
        """
        Index a data source catalog for search and retrieval.

        This method now delegates to the unified indexing service to avoid duplication.

        Args:
            data_source_id: ID of the data source
            datasource: DataSource instance
            index_level: Level of indexing (catalog, schema, table, column)
            catalog_id: Optional custom catalog ID

        Returns:
            str: The catalog ID

        Raises:
            CatalogIndexError: If indexing fails
        """
        try:
            # Use the unified indexing service
            catalog_id = self._index_service.index_datasource(
                datasource=datasource,
                data_source_id=data_source_id,
                level=index_level,  # type: ignore
                catalog_id=catalog_id,
            )

            # Load the indexed catalog into cache
            self._load_catalog_to_cache(catalog_id)

            return catalog_id

        except Exception as e:
            logger.error(f"Failed to index catalog: {str(e)}")
            raise CatalogIndexError("index", catalog_id or "unknown", e)

    def _load_catalog_to_cache(self, catalog_id: str) -> None:
        """Load catalog and its index into cache after indexing."""
        try:
            # Load catalog index
            index_key = f"{self._metadata_prefix}{catalog_id}"
            index_data = self.metadata_store.mget([index_key])[0]
            if index_data:
                index_dict = json.loads(index_data)
                self._index_cache[catalog_id] = CatalogIndex.from_dict(index_dict)

            # Load catalog data
            catalog_key = f"{self._catalog_prefix}{catalog_id}"
            catalog_data = self.metadata_store.mget([catalog_key])[0]
            if catalog_data:
                catalog_dict = json.loads(catalog_data)
                self._catalog_cache[catalog_id] = self._deserialize_catalog(
                    catalog_dict
                )
        except Exception as e:
            logger.warning(f"Failed to load catalog {catalog_id} to cache: {e}")

    # Note: _index_catalog_vectors method has been removed as indexing is now handled
    # by the UnifiedCatalogIndexService to avoid duplication

    def search_catalogs(
        self,
        query: str,
        top_k: int = 10,
        catalog_ids: Optional[List[str]] = None,
        element_type: Optional[str] = None,  # catalog, schema, table, column
    ) -> List[Dict[str, Any]]:
        """
        Search catalogs using semantic similarity.

        Args:
            query: Search query
            top_k: Number of results to return
            catalog_ids: Limit search to specific catalog IDs
            element_type: Limit search to specific element types

        Returns:
            List of search results with metadata

        Raises:
            StoreException: If search fails or vector store not available
        """
        if not self.vector_store:
            raise StoreException("Vector store not available for catalog search")

        try:
            # Build filter for metadata
            filter_dict = {}
            if catalog_ids:
                filter_dict["catalog_id"] = {"$in": catalog_ids}
            if element_type:
                filter_dict["type"] = element_type

            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(
                query, k=top_k, filter=filter_dict if filter_dict else None
            )

            # Format results
            search_results = []
            for doc, score in results:
                result = {
                    "content": doc.page_content,
                    "score": score,
                    "metadata": doc.metadata,
                }
                search_results.append(result)

            return search_results

        except Exception as e:
            raise StoreException(f"Catalog search failed: {str(e)}", e)

    def get_catalog(self, catalog_id: str) -> Catalog:
        """
        Retrieve a catalog by ID.

        Args:
            catalog_id: The catalog ID

        Returns:
            Catalog: The catalog object

        Raises:
            CatalogNotFoundError: If catalog is not found
        """
        # Check cache first
        if catalog_id in self._catalog_cache:
            return self._catalog_cache[catalog_id]

        try:
            # Load from store
            catalog_key = f"{self._catalog_prefix}{catalog_id}"
            data = self.metadata_store.mget([catalog_key])[0]
            if not data:
                raise CatalogNotFoundError(catalog_id)

            catalog_data = json.loads(data)
            catalog = self._deserialize_catalog(catalog_data)

            # Cache it
            self._catalog_cache[catalog_id] = catalog
            return catalog

        except CatalogNotFoundError:
            raise
        except Exception as e:
            raise CatalogNotFoundError(catalog_id, cause=e)

    def get_catalog_index(self, catalog_id: str) -> CatalogIndex:
        """
        Get catalog index metadata.

        Args:
            catalog_id: The catalog ID

        Returns:
            CatalogIndex: The catalog index metadata

        Raises:
            CatalogNotFoundError: If catalog index is not found
        """
        if catalog_id in self._index_cache:
            return self._index_cache[catalog_id]

        try:
            index_key = f"{self._metadata_prefix}{catalog_id}"
            data = self.metadata_store.mget([index_key])[0]
            if not data:
                raise CatalogNotFoundError(catalog_id)

            index_dict = json.loads(data)
            catalog_index = CatalogIndex.from_dict(index_dict)

            # Cache it
            self._index_cache[catalog_id] = catalog_index
            return catalog_index

        except CatalogNotFoundError:
            raise
        except Exception as e:
            raise CatalogNotFoundError(catalog_id, cause=e)

    def list_catalog_indexes(
        self, data_source_id: Optional[str] = None
    ) -> List[CatalogIndex]:
        """
        List all catalog indexes, optionally filtered by data source.

        Args:
            data_source_id: Optional data source ID filter

        Returns:
            List[CatalogIndex]: List of catalog indexes
        """
        indexes = list(self._index_cache.values())

        if data_source_id:
            indexes = [idx for idx in indexes if idx.data_source_id == data_source_id]

        return indexes

    def remove_catalog(self, catalog_id: str) -> None:
        """
        Remove a catalog and its index.

        Args:
            catalog_id: The catalog ID

        Raises:
            CatalogNotFoundError: If catalog is not found
            StoreException: If removal fails
        """
        # Check if exists
        self.get_catalog_index(catalog_id)

        try:
            # Remove from metadata store
            index_key = f"{self._metadata_prefix}{catalog_id}"
            catalog_key = f"{self._catalog_prefix}{catalog_id}"
            self.metadata_store.mdelete([index_key, catalog_key])

            # Remove from vector store if available
            if self.vector_store:
                try:
                    # Delete all vectors for this catalog
                    # The catalog_id is prefixed to all vector IDs by the indexer
                    if hasattr(self.vector_store, "delete"):
                        self.vector_store.delete(filter={"catalog_id": catalog_id})
                except Exception as e:
                    logger.warning(
                        f"Failed to remove vectors for catalog {catalog_id}: {e}"
                    )

            # Remove from caches
            self._catalog_cache.pop(catalog_id, None)
            self._index_cache.pop(catalog_id, None)

            logger.info(f"Removed catalog: {catalog_id}")

        except Exception as e:
            raise StoreException(f"Failed to remove catalog '{catalog_id}'", e)

    def _serialize_catalog(self, catalog: Catalog) -> Dict[str, Any]:
        """Serialize catalog to dictionary for storage."""
        return {
            "catalog_name": catalog.catalog_name,
            "schemas": [
                {
                    "schema_name": schema.schema_name,
                    "tables": [
                        {
                            "table_name": table.table_name,
                            "columns": [
                                {
                                    "name": col.name,
                                    "type": col.type,
                                    "nullable": col.nullable,
                                    "description": col.description,
                                }
                                for col in table.columns
                            ],
                        }
                        for table in schema.tables
                    ],
                }
                for schema in catalog.schemas
            ],
        }

    def _deserialize_catalog(self, data: Dict[str, Any]) -> Catalog:
        """Deserialize catalog from dictionary."""
        schemas = []
        for schema_data in data["schemas"]:
            tables = []
            for table_data in schema_data["tables"]:
                columns = [
                    Column(
                        name=col_data["name"],
                        type=col_data["type"],
                        nullable=col_data.get("nullable", True),
                        description=col_data.get("description"),
                    )
                    for col_data in table_data["columns"]
                ]
                tables.append(
                    Table(table_name=table_data["table_name"], columns=columns)
                )
            schemas.append(
                Schema(schema_name=schema_data["schema_name"], tables=tables)
            )

        return Catalog(catalog_name=data["catalog_name"], schemas=schemas)

    def clear_cache(self) -> None:
        """Clear all cached catalog data."""
        self._catalog_cache.clear()
        self._index_cache.clear()
        logger.info("Cleared catalog cache")

    def search_relevant_catalog(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.3,
        element_types: Optional[List[str]] = None,
    ) -> Catalog:
        """
        Search for relevant catalog elements using only indexed metadata.

        Args:
            query: User question or search query
            top_k: Maximum number of results to consider
            min_score: Minimum similarity score for relevance
            element_types: Types to search for ["table", "schema", "column"]

        Returns:
            Catalog containing only relevant metadata from search results

        Raises:
            CatalogNotIndexedError: If no catalog store or no indexed catalogs available
        """
        if not self.vector_store:
            raise CatalogNotIndexedError(
                "Vector store is required for optimized search. Please index your catalogs first."
            )

        try:
            # Search for relevant elements using semantic similarity
            search_results = self.search_catalogs(
                query=query,
                top_k=top_k,
                element_type=None,  # Search all types initially
            )

            if not search_results:
                logger.info(f"No indexed catalog results found for query: '{query}'")
                return Catalog(catalog_name="empty_search_result", schemas=[])

            # Extract and build catalog from search results only
            optimized_catalog = self._build_catalog_from_search_results(
                search_results, min_score, element_types
            )

            logger.info(
                f"Optimized catalog search: {len(search_results)} results → "
                f"{sum(len(s.tables) for s in optimized_catalog.schemas)} tables"
            )

            return optimized_catalog

        except StoreException as e:
            raise CatalogNotIndexedError(
                f"Catalog search failed. Please ensure catalogs are properly indexed: {e}"
            )

    def _build_catalog_from_search_results(
        self,
        search_results: List[Dict],
        min_score: float,
        element_types: Optional[List[str]],
    ) -> Catalog:
        """
        Build catalog directly from search results without additional data loading.

        This constructs the catalog metadata entirely from what's available
        in the search results, avoiding any database queries.
        """
        # Group results by schema and table
        schema_data = {}

        for result in search_results:
            score = result.get("score", 0.0)
            if score < min_score:
                continue

            metadata = result.get("metadata", {})
            element_type = metadata.get("type")

            # Skip if filtering by specific element types
            if element_types and element_type not in element_types:
                continue

            schema_name = metadata.get("schema_name")
            table_name = metadata.get("table_name")
            column_name = metadata.get("name")

            if not schema_name:
                continue

            # Initialize schema if not exists
            if schema_name not in schema_data:
                schema_data[schema_name] = {"tables": {}}

            if element_type == "table" and table_name:
                # Add table metadata from search result
                if table_name not in schema_data[schema_name]["tables"]:
                    schema_data[schema_name]["tables"][table_name] = {
                        "columns": [],
                        "metadata": metadata,
                        "description": result.get("content", ""),
                    }

            elif element_type == "column" and table_name and column_name:
                # Add table if not exists
                if table_name not in schema_data[schema_name]["tables"]:
                    schema_data[schema_name]["tables"][table_name] = {
                        "columns": [],
                        "metadata": {},
                        "description": "",
                    }

                # Add column metadata
                column_info = {
                    "name": column_name,
                    "type": metadata.get("data_type", "unknown"),
                    "nullable": metadata.get("nullable", True),
                    "description": result.get("content", ""),
                }
                schema_data[schema_name]["tables"][table_name]["columns"].append(
                    column_info
                )

        # Build Schema and Table objects
        schemas = []
        for schema_name, schema_info in schema_data.items():
            tables = []

            for table_name, table_info in schema_info["tables"].items():
                # Build columns
                columns = []
                for col_info in table_info["columns"]:
                    columns.append(
                        Column(
                            name=col_info["name"],
                            type=col_info["type"],
                            nullable=col_info["nullable"],
                            description=col_info["description"],
                        )
                    )

                # Create table
                tables.append(
                    Table(
                        table_name=table_name,
                        columns=columns,
                    )
                )

            # Create schema
            if tables:  # Only add schemas that have tables
                schemas.append(
                    Schema(
                        schema_name=schema_name,
                        tables=tables,
                    )
                )

        # Determine catalog name from first available catalog
        catalog_name = "search_results"
        if self._index_cache:
            first_index = next(iter(self._index_cache.values()))
            catalog_name = first_index.catalog_name

        return Catalog(
            catalog_name=catalog_name,
            schemas=schemas,
        )

    def get_table_suggestions(
        self,
        query: str,
        max_tables: int = 5,
        min_score: float = 0.4,
    ) -> List[Dict[str, str]]:
        """
        Get table suggestions for a query based on indexed metadata.

        Args:
            query: Search query
            max_tables: Maximum number of table suggestions
            min_score: Minimum similarity score

        Returns:
            List of table suggestions with metadata

        Raises:
            CatalogNotIndexedError: If catalog store is not available
        """
        if not self.vector_store:
            raise CatalogNotIndexedError(
                "Vector store is required for table suggestions. Please index your catalogs first."
            )

        try:
            search_results = self.search_catalogs(
                query=query,
                top_k=max_tables * 2,  # Get more results to filter
                element_type="table",
            )

            suggestions = []
            for result in search_results:
                score = result.get("score", 0.0)
                if score < min_score:
                    continue

                metadata = result.get("metadata", {})
                schema_name = metadata.get("schema_name")
                table_name = metadata.get("name")

                if schema_name and table_name:
                    suggestions.append(
                        {
                            "schema": schema_name,
                            "table": table_name,
                            "score": score,
                            "description": result.get("content", ""),
                            "full_name": f"{schema_name}.{table_name}",
                            "column_count": metadata.get("column_count", 0),
                        }
                    )

                if len(suggestions) >= max_tables:
                    break

            return suggestions

        except StoreException as e:
            raise CatalogNotIndexedError(
                f"Failed to get table suggestions. Ensure catalogs are indexed: {e}"
            )

    def get_column_suggestions(
        self,
        query: str,
        table_context: Optional[str] = None,
        max_columns: int = 10,
        min_score: float = 0.3,
    ) -> List[Dict[str, str]]:
        """
        Get column suggestions for a query based on indexed metadata.

        Args:
            query: Search query
            table_context: Optional table name to filter results
            max_columns: Maximum number of column suggestions
            min_score: Minimum similarity score

        Returns:
            List of column suggestions with metadata
        """
        if not self.vector_store:
            raise CatalogNotIndexedError(
                "Vector store is required for column suggestions. Please index your catalogs first."
            )

        try:
            search_results = self.search_catalogs(
                query=query,
                top_k=max_columns * 2,
                element_type="column",
            )

            suggestions = []
            for result in search_results:
                score = result.get("score", 0.0)
                if score < min_score:
                    continue

                metadata = result.get("metadata", {})
                schema_name = metadata.get("schema_name")
                table_name = metadata.get("table_name")
                column_name = metadata.get("name")

                # Filter by table context if provided
                if table_context and table_name != table_context:
                    continue

                if schema_name and table_name and column_name:
                    suggestions.append(
                        {
                            "schema": schema_name,
                            "table": table_name,
                            "column": column_name,
                            "score": score,
                            "description": result.get("content", ""),
                            "full_name": f"{schema_name}.{table_name}.{column_name}",
                            "data_type": metadata.get("data_type", "unknown"),
                            "nullable": metadata.get("nullable", True),
                        }
                    )

                if len(suggestions) >= max_columns:
                    break

            return suggestions

        except StoreException as e:
            raise CatalogNotIndexedError(
                f"Failed to get column suggestions. Ensure catalogs are indexed: {e}"
            )

    def validate_indexing_status(self) -> Dict[str, Any]:
        """
        Check if catalogs are properly indexed.

        Returns:
            Dictionary with indexing status information
        """
        if not self.vector_store:
            return {
                "has_vector_store": False,
                "has_indexed_catalogs": False,
                "catalog_count": 0,
                "error": "No vector store configured",
            }

        try:
            indexes = self.list_catalog_indexes()
            return {
                "has_vector_store": True,
                "has_indexed_catalogs": len(indexes) > 0,
                "catalog_count": len(indexes),
                "indexed_catalogs": [
                    idx.catalog_name for idx in indexes[:5]
                ],  # Show first 5
            }
        except Exception as e:
            return {
                "has_vector_store": True,
                "has_indexed_catalogs": False,
                "catalog_count": 0,
                "error": str(e),
            }
