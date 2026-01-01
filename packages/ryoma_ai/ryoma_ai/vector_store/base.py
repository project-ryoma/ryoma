import logging
from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

from databuilder.loader.base_loader import Loader
from databuilder.loader.generic_loader import GenericLoader
from databuilder.models.table_metadata import TableMetadata
from pyhocon import ConfigTree
from ryoma_data.metadata import Catalog, Column, Schema, Table


@dataclass
class SearchResult:
    id: str
    score: float
    metadata: Dict[str, Any]


class VectorStore(ABC):
    def index(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add or update vector entries with corresponding metadata.
        Useful for decoupling from embedding logic (embed first, then index).
        """
        raise NotImplementedError

    def index_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Embed and add text documents to the vector store.
        """
        raise NotImplementedError

    def search(self, query_vector: List[float], top_k: int = 5) -> List[SearchResult]:
        """
        Perform vector-based semantic search using a precomputed query vector.
        Returns a list of SearchResult, each with ID, score, and metadata (e.g. text).
        """
        raise NotImplementedError

    def search_documents(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Embed the query and return semantically similar results from the vector store.
        """
        raise NotImplementedError

    def _record_indexer(self) -> Loader:
        class SessionLoader(GenericLoader):
            def __init__(self, callback_func):
                self._callback_func = callback_func

            def init(self, conf: ConfigTree) -> None:
                self.conf = conf
                self._callback_func = self._callback_func

        return SessionLoader(self._index_catalog_record)

    def _index_catalog_record(self, record: TableMetadata):
        """
        Index catalog entry to the vector store.
        """
        logging.info(f"Indexing catalog entry to vector store: {record}")
        self.index_documents(
            ids=[record.name],
            documents=[
                (
                    record.description.text
                    if record.description
                    else "No description available"
                )
            ],
            metadatas=[
                {
                    "columns": [col.name for col in record.columns],
                    "schema": record.schema,
                    "is_view": record.is_view,
                    "attrs": str(record.attrs),
                }
            ],
        )

    def _build_id(
        self,
        catalog: Catalog,
        schema: Optional[Schema] = None,
        table: Optional[Table] = None,
        column: Optional[Column] = None,
    ) -> str:
        """
        Build an ID string from catalog, schema, table, column name and type.
        """
        id = f"{catalog.catalog_name}"
        if schema:
            id += f".{schema.schema_name}"
        if table:
            id += f".{table.table_name}"
        if column:
            id += f".{column.name}"
        return id

    def _build_document(
        self,
        catalog: Catalog,
        level: Literal["catalog", "schema", "table", "column"] = "catalog",
        schema: Optional[Schema] = None,
        table: Optional[Table] = None,
        column: Optional[Column] = None,
    ) -> str:
        """
        Build a document string from catalog, schema, table, column name and type.
        """
        res = f"Catalog: {catalog.catalog_name}"
        if level == catalog:
            return res + str(catalog)
        res += schema.schema_name
        if level == "schema":
            return res + str(schema)
        res += table.table_name
        if level == "table":
            return res + str(table)
        return res + (
            f"\nColumn: {column.column_name}"
            + f"\nType: {column.column_type}"
            + f"\nNullable: {column.nullable}"
            + f"\nDescription: {column.description or 'No description available'}"
        )

    def retrieve_columns(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Column]:
        """
        Search the catalog of a data source and return the top k similar columns.
        """
        results = self.search_documents(query, top_k)
        columns = []
        for result in results:
            metadata = result.metadata
            column = Column(
                column_name=result.id,
                column_type=metadata.get("column_type", "unknown"),
                nullable=metadata.get("nullable", False),
                description=metadata.get("description", ""),
            )
            columns.append(column)
        return columns
