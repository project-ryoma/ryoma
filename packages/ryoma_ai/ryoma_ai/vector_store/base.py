import logging
from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from databuilder.loader.base_loader import Loader
from databuilder.loader.generic_loader import GenericLoader
from databuilder.models.table_metadata import TableMetadata
from pyhocon import ConfigTree
from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.metadata import Catalog, Column, Schema, Table


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

    def index_datasource(
        self,
        datasource: DataSource,
        on_demand: bool = True,
    ) -> None:
        """
        Index Catalog from a data source into the vector store.
        """
        if on_demand:
            catalog = datasource.get_catalog()
            for schema in catalog.schemas:
                for table in schema.tables:
                    for column in table.columns:
                        document = self._build_document(
                            catalog,
                            schema,
                            table,
                            column,
                        )
                        self.index_documents(
                            ids=[self._build_id(catalog, schema, table, column)],
                            documents=[document],
                        )
        else:
            logging.info(
                f"Start crawling metadata for datasource {datasource} and indexing"
            )
            datasource.crawl_catalogs(
                loader=self._record_indexer(),
            )

    def _build_id(
        self,
        catalog: Catalog,
        schema: Schema,
        table: Table,
        column: Column,
    ) -> str:
        """
        Build an ID string from catalog, schema, table, column name and type.
        """
        return f"{catalog.catalog_name}.{schema.schema_name}.{table.table_name}.{column.column_name}"

    def _build_document(
        self,
        catalog: Catalog,
        schema: Schema,
        table: Table,
        column: Column,
    ) -> str:
        """
        Build a document string from catalog, schema, table, column name and type.
        """
        return (
            f"Catalog: {catalog.catalog_name}"
            + f"\nSchema: {schema.schema_name}"
            + f"\nTable: {table.table_name}"
            + f"\nColumn: {column.column_name}"
            + f"\nType: {column.column_type}"
            + f"\nNullable: {column.nullable}"
            + f"\nDescription: {column.description or 'No description available'}"
        )

    def search_datasource_catalog(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[SearchResult]:
        """
        Search the catalog of a data source.
        """
        return self.search_documents(query, top_k)
