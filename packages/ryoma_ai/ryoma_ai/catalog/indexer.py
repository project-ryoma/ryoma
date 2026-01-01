"""
Unified catalog indexing module that combines structured storage and vector indexing.

This module provides a single interface for indexing data source catalogs,
replacing the duplicate implementations in vector_store.base and catalog_store.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Protocol, Tuple

from langchain_core.stores import BaseStore
from langchain_core.vectorstores import VectorStore
from ryoma_ai.catalog.exceptions import CatalogIndexError
from ryoma_data.base import DataSource
from ryoma_data.metadata import Catalog, Column, Schema, Table
from ryoma_ai.models.catalog import CatalogIndex

logger = logging.getLogger(__name__)

IndexLevel = Literal["catalog", "schema", "table", "column"]


class VectorIndexer(Protocol):
    """Protocol for vector indexing functionality."""

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add texts to the vector index."""
        ...


class CatalogIndexer(ABC):
    """Abstract base class for catalog indexing strategies."""

    @abstractmethod
    def index(
        self,
        catalog: Catalog,
        catalog_id: str,
        data_source_id: str,
        level: IndexLevel = "table",
    ) -> CatalogIndex:
        """Index a catalog at the specified level."""
        pass

    @abstractmethod
    def get_indexed_elements(
        self, catalog: Catalog, level: IndexLevel
    ) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Get elements to be indexed as (id, document, metadata) tuples."""
        pass


class HierarchicalCatalogIndexer(CatalogIndexer):
    """
    Indexes catalog hierarchically with proper ID generation and document formatting.

    This indexer creates searchable documents for each level of the catalog hierarchy:
    - Catalog level: Overall catalog information
    - Schema level: Schema with table counts
    - Table level: Table with column summaries
    - Column level: Individual column details
    """

    def __init__(
        self,
        vector_store: Optional[VectorIndexer] = None,
        metadata_store: Optional[BaseStore[str, str]] = None,
    ):
        """
        Initialize the hierarchical catalog indexer.

        Args:
            vector_store: Optional vector store for semantic search
            metadata_store: Optional metadata store for structured storage
        """
        self.vector_store = vector_store
        self.metadata_store = metadata_store

    def index(
        self,
        catalog: Catalog,
        catalog_id: str,
        data_source_id: str,
        level: IndexLevel = "table",
    ) -> CatalogIndex:
        """
        Index a catalog hierarchically up to the specified level.

        Args:
            catalog: The catalog to index
            catalog_id: Unique identifier for this catalog index
            data_source_id: ID of the source data source
            level: Maximum depth to index ("catalog", "schema", "table", "column")

        Returns:
            CatalogIndex with indexing metadata
        """
        # Count elements
        schema_count = len(catalog.schemas) if catalog.schemas else 0
        table_count = sum(len(schema.tables) for schema in (catalog.schemas or []))
        column_count = sum(
            len(table.columns)
            for schema in (catalog.schemas or [])
            for table in (schema.tables or [])
        )

        # Store catalog metadata if metadata store is available
        if self.metadata_store:
            catalog_data = self._serialize_catalog(catalog)
            catalog_key = f"catalog_data:{catalog_id}"
            self.metadata_store.mset([(catalog_key, json.dumps(catalog_data))])

        # Index in vector store if available
        if self.vector_store:
            elements = self.get_indexed_elements(catalog, level)
            if elements:
                ids, documents, metadatas = zip(*elements)
                # Add catalog_id to all metadata
                enhanced_metadatas = [
                    {
                        **metadata,
                        "catalog_id": catalog_id,
                        "data_source_id": data_source_id,
                    }
                    for metadata in metadatas
                ]
                self.vector_store.add_texts(
                    texts=list(documents),
                    metadatas=enhanced_metadatas,
                    ids=[f"{catalog_id}_{id_}" for id_ in ids],
                )

        # Create index record
        catalog_index = CatalogIndex(
            catalog_id=catalog_id,
            data_source_id=data_source_id,
            catalog_name=catalog.catalog_name,
            indexed_at=datetime.now(),
            schema_count=schema_count,
            table_count=table_count,
            column_count=column_count,
            index_level=level,
        )

        # Store index metadata if metadata store is available
        if self.metadata_store:
            index_key = f"catalog_meta:{catalog_id}"
            self.metadata_store.mset([(index_key, json.dumps(catalog_index.to_dict()))])

        logger.info(
            f"Indexed catalog '{catalog.catalog_name}' (ID: {catalog_id}) "
            f"at level '{level}' with {len(elements) if self.vector_store else 0} vectors"
        )

        return catalog_index

    def get_indexed_elements(
        self, catalog: Catalog, level: IndexLevel
    ) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Get all elements to be indexed up to the specified level.

        Returns list of tuples: (element_id, document_text, metadata_dict)
        """
        elements = []

        # Always index catalog level
        elements.append(self._create_catalog_element(catalog))

        if level == "catalog":
            return elements

        # Index schemas
        for schema in catalog.schemas or []:
            elements.append(self._create_schema_element(catalog, schema))

            if level == "schema":
                continue

            # Index tables
            for table in schema.tables or []:
                elements.append(self._create_table_element(catalog, schema, table))

                if level == "table":
                    continue

                # Index columns
                for column in table.columns or []:
                    elements.append(
                        self._create_column_element(catalog, schema, table, column)
                    )

        return elements

    def _create_catalog_element(
        self, catalog: Catalog
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Create indexable element for a catalog."""
        schema_names = [s.schema_name for s in (catalog.schemas or [])]
        document = (
            f"Catalog: {catalog.catalog_name}\n"
            f"Schemas: {len(schema_names)} ({', '.join(schema_names[:5])}"
            f"{'...' if len(schema_names) > 5 else ''})"
        )

        metadata = {
            "type": "catalog",
            "name": catalog.catalog_name,
            "schema_count": len(catalog.schemas or []),
        }

        return f"catalog_{catalog.catalog_name}", document, metadata

    def _create_schema_element(
        self, catalog: Catalog, schema: Schema
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Create indexable element for a schema."""
        table_names = [t.table_name for t in (schema.tables or [])]
        document = (
            f"Schema: {catalog.catalog_name}.{schema.schema_name}\n"
            f"Tables: {len(table_names)} ({', '.join(table_names[:5])}"
            f"{'...' if len(table_names) > 5 else ''})"
        )

        metadata = {
            "type": "schema",
            "name": schema.schema_name,
            "catalog_name": catalog.catalog_name,
            "table_count": len(schema.tables or []),
        }

        return f"schema_{schema.schema_name}", document, metadata

    def _create_table_element(
        self, catalog: Catalog, schema: Schema, table: Table
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Create indexable element for a table."""
        columns_desc = ", ".join(
            [f"{col.name}({col.type})" for col in (table.columns or [])[:5]]
        )
        if len(table.columns or []) > 5:
            columns_desc += f" ... (+{len(table.columns) - 5} more)"

        document = (
            f"Table: {catalog.catalog_name}.{schema.schema_name}.{table.table_name}\n"
            f"Columns: {columns_desc}"
        )

        metadata = {
            "type": "table",
            "name": table.table_name,
            "catalog_name": catalog.catalog_name,
            "schema_name": schema.schema_name,
            "column_count": len(table.columns or []),
            "column_names": [col.name for col in (table.columns or [])],
        }

        return f"table_{schema.schema_name}_{table.table_name}", document, metadata

    def _create_column_element(
        self, catalog: Catalog, schema: Schema, table: Table, column: Column
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Create indexable element for a column."""
        document = (
            f"Column: {catalog.catalog_name}.{schema.schema_name}."
            f"{table.table_name}.{column.name}\n"
            f"Type: {column.type}\n"
            f"Nullable: {'Yes' if column.nullable else 'No'}\n"
            f"Description: {column.description or 'No description available'}"
        )

        metadata = {
            "type": "column",
            "name": column.name,
            "catalog_name": catalog.catalog_name,
            "schema_name": schema.schema_name,
            "table_name": table.table_name,
            "data_type": column.type,
            "nullable": column.nullable,
            "description": column.description,
        }

        return (
            f"column_{schema.schema_name}_{table.table_name}_{column.name}",
            document,
            metadata,
        )

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
                                for col in (table.columns or [])
                            ],
                        }
                        for table in (schema.tables or [])
                    ],
                }
                for schema in (catalog.schemas or [])
            ],
        }


class UnifiedCatalogIndexService:
    """
    This service provides a single entry point for all catalog indexing needs,
    supporting both structured metadata storage and vector-based semantic search.
    """

    def __init__(
        self,
        indexer: Optional[CatalogIndexer] = None,
        vector_store: Optional[VectorStore] = None,
        metadata_store: Optional[BaseStore[str, str]] = None,
    ):
        """
        Initialize the unified catalog index service.

        Args:
            indexer: Custom indexer implementation (defaults to HierarchicalCatalogIndexer)
            vector_store: Vector store for semantic search
            metadata_store: Metadata store for structured storage
        """
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self.indexer = indexer or HierarchicalCatalogIndexer(
            vector_store=vector_store,
            metadata_store=metadata_store,
        )

    def index_datasource(
        self,
        datasource: DataSource,
        data_source_id: str,
        level: IndexLevel = "table",
        catalog_id: Optional[str] = None,
    ) -> str:
        """
        Index a data source catalog.

        This is the main entry point for catalog indexing, replacing both
        vector_store.index_datasource() and catalog_store.index_catalog().

        Args:
            datasource: The data source to index
            data_source_id: ID of the data source
            level: Level to index up to ("catalog", "schema", "table", "column")
            catalog_id: Optional custom catalog ID

        Returns:
            The catalog ID

        Raises:
            CatalogIndexError: If indexing fails
        """
        try:
            # Get catalog from data source
            catalog = datasource.get_catalog()

            # Generate catalog ID if not provided
            if not catalog_id:
                catalog_id = (
                    f"{data_source_id}_{catalog.catalog_name}_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

            # Perform indexing
            catalog_index = self.indexer.index(
                catalog=catalog,
                catalog_id=catalog_id,
                data_source_id=data_source_id,
                level=level,
            )

            return catalog_index.catalog_id

        except Exception as e:
            logger.error(f"Failed to index datasource: {str(e)}")
            raise CatalogIndexError("index", catalog_id or "unknown", e)
