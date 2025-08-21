"""
Catalog store using LangChain stores and vector stores for indexing and search.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging

from langchain_core.stores import BaseStore, InMemoryStore
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings

from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.metadata import Catalog, Schema, Table, Column
from ryoma_ai.store.exceptions import (
    CatalogNotFoundError,
    CatalogIndexError,
    StoreException
)
from ryoma_ai.models.catalog import CatalogIndex

logger = logging.getLogger(__name__)


class CatalogStore:
    """
    Store for managing and indexing data source catalogs using LangChain stores.

    Provides catalog indexing, search, and metadata management with both
    structured storage and vector-based semantic search capabilities.
    """

    def __init__(
        self,
        metadata_store: Optional[BaseStore[str, str]] = None,
        vector_store: Optional[VectorStore] = None,
        embedding_function: Optional[Embeddings] = None
    ):
        """
        Initialize the catalog store.

        Args:
            metadata_store: LangChain BaseStore for catalog metadata
            vector_store: LangChain VectorStore for semantic search
            embedding_function: Embeddings for vector indexing
        """
        self.metadata_store: BaseStore[str, str] = metadata_store or InMemoryStore()
        self.vector_store = vector_store
        self.embedding_function = embedding_function

        self._catalog_cache: Dict[str, Catalog] = {}
        self._index_cache: Dict[str, CatalogIndex] = {}
        self._metadata_prefix = "catalog_meta:"
        self._catalog_prefix = "catalog_data:"

        # Load existing indexes
        self._load_indexes()

    def _load_indexes(self) -> None:
        """Load existing catalog indexes from metadata store."""
        try:
            all_keys = []
            try:
                if hasattr(self.metadata_store, 'yield_keys'):
                    all_keys = list(self.metadata_store.yield_keys())
                elif hasattr(self.metadata_store, 'keys'):
                    all_keys = list(self.metadata_store.keys())
            except Exception:
                pass

            index_keys = [key for key in all_keys if key.startswith(self._metadata_prefix)]

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
        catalog_id: Optional[str] = None
    ) -> str:
        """
        Index a data source catalog for search and retrieval.

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
            # Get catalog from data source
            catalog = datasource.get_catalog()

            if not catalog_id:
                catalog_id = f"{data_source_id}_{catalog.catalog_name}_{datetime.now().isoformat()}"

            # Count elements
            schema_count = len(catalog.schemas)
            table_count = sum(len(schema.tables) for schema in catalog.schemas)
            column_count = sum(
                len(table.columns)
                for schema in catalog.schemas
                for table in schema.tables
            )

            # Store catalog data
            catalog_key = f"{self._catalog_prefix}{catalog_id}"
            catalog_data = self._serialize_catalog(catalog)
            self.metadata_store.mset([(catalog_key, json.dumps(catalog_data))])

            # Index in vector store if available
            if self.vector_store and self.embedding_function:
                self._index_catalog_vectors(catalog, catalog_id, index_level)

            # Create and store index metadata
            catalog_index = CatalogIndex(
                catalog_id=catalog_id,
                data_source_id=data_source_id,
                catalog_name=catalog.catalog_name,
                indexed_at=datetime.now(),
                schema_count=schema_count,
                table_count=table_count,
                column_count=column_count,
                index_level=index_level
            )

            index_key = f"{self._metadata_prefix}{catalog_id}"
            self.metadata_store.mset([(index_key, json.dumps(catalog_index.to_dict()))])

            # Update caches
            self._catalog_cache[catalog_id] = catalog
            self._index_cache[catalog_id] = catalog_index

            logger.info(f"Indexed catalog: {catalog_id} at level {index_level}")
            return catalog_id

        except Exception as e:
            raise CatalogIndexError("index", catalog_id or "unknown", e)

    def _index_catalog_vectors(
        self,
        catalog: Catalog,
        catalog_id: str,
        level: str
    ) -> None:
        """Index catalog in vector store for semantic search."""
        documents = []
        metadatas = []
        ids = []

        if level == "catalog":
            doc = f"Catalog: {catalog.catalog_name}\nSchemas: {len(catalog.schemas)}"
            documents.append(doc)
            metadatas.append({
                "catalog_id": catalog_id,
                "type": "catalog",
                "name": catalog.catalog_name
            })
            ids.append(f"{catalog_id}_catalog")

        elif level in ["schema", "table", "column"]:
            for schema in catalog.schemas:
                if level == "schema":
                    doc = f"Schema: {schema.schema_name}\nTables: {len(schema.tables)}"
                    documents.append(doc)
                    metadatas.append({
                        "catalog_id": catalog_id,
                        "type": "schema",
                        "name": schema.schema_name,
                        "schema": schema.schema_name
                    })
                    ids.append(f"{catalog_id}_schema_{schema.schema_name}")

                elif level in ["table", "column"]:
                    for table in schema.tables:
                        if level == "table":
                            columns_desc = ", ".join([f"{col.name}({col.type})" for col in table.columns[:5]])
                            if len(table.columns) > 5:
                                columns_desc += f" ... (+{len(table.columns) - 5} more)"

                            doc = f"Table: {schema.schema_name}.{table.table_name}\nColumns: {columns_desc}"
                            documents.append(doc)
                            metadatas.append({
                                "catalog_id": catalog_id,
                                "type": "table",
                                "name": table.table_name,
                                "schema": schema.schema_name,
                                "table": table.table_name
                            })
                            ids.append(f"{catalog_id}_table_{schema.schema_name}_{table.table_name}")

                        elif level == "column":
                            for column in table.columns:
                                doc = f"Column: {schema.schema_name}.{table.table_name}.{column.name}\nType: {column.type}\nDescription: {column.description or 'No description'}"
                                documents.append(doc)
                                metadatas.append({
                                    "catalog_id": catalog_id,
                                    "type": "column",
                                    "name": column.name,
                                    "schema": schema.schema_name,
                                    "table": table.table_name,
                                    "column": column.name,
                                    "data_type": column.type
                                })
                                ids.append(f"{catalog_id}_column_{schema.schema_name}_{table.table_name}_{column.name}")

        # Add documents to vector store
        if documents:
            self.vector_store.add_texts(
                texts=documents,
                metadatas=metadatas,
                ids=ids
            )

    def search_catalogs(
        self,
        query: str,
        top_k: int = 10,
        catalog_ids: Optional[List[str]] = None,
        element_type: Optional[str] = None  # catalog, schema, table, column
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
                query,
                k=top_k,
                filter=filter_dict if filter_dict else None
            )

            # Format results
            search_results = []
            for doc, score in results:
                result = {
                    "content": doc.page_content,
                    "score": score,
                    "metadata": doc.metadata
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
        self,
        data_source_id: Optional[str] = None
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
                    self.vector_store.delete(
                        filter={"catalog_id": catalog_id}
                    )
                except Exception as e:
                    logger.warning(f"Failed to remove vectors for catalog {catalog_id}: {e}")

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
                                    "description": col.description
                                }
                                for col in table.columns
                            ]
                        }
                        for table in schema.tables
                    ]
                }
                for schema in catalog.schemas
            ]
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
                        description=col_data.get("description")
                    )
                    for col_data in table_data["columns"]
                ]
                tables.append(Table(
                    table_name=table_data["table_name"],
                    columns=columns
                ))
            schemas.append(Schema(
                schema_name=schema_data["schema_name"],
                tables=tables
            ))

        return Catalog(
            catalog_name=data["catalog_name"],
            schemas=schemas
        )

    def clear_cache(self) -> None:
        """Clear all cached catalog data."""
        self._catalog_cache.clear()
        self._index_cache.clear()
        logger.info("Cleared catalog cache")
