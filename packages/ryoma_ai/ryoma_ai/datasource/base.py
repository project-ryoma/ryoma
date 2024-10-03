import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from ibis import Table as IbisTable
from ibis.backends import CanListCatalog, CanListDatabase
from ibis.backends.sql import SQLBackend
from ryoma_ai.datasource.metadata import Catalog, Column, Schema, Table


class DataSource(ABC):
    def __init__(self, type: str, **kwargs):
        self.type = type

    @abstractmethod
    def get_catalog(self, **kwargs):
        raise NotImplementedError("get_catalog is not implemented for this data source")


class SqlDataSource(DataSource):
    def __init__(self, database: Optional[str] = None, db_schema: Optional[str] = None):
        super().__init__(type="sql")
        self.database = database
        self.db_schema = db_schema
        self.__connection = None

    def connect(self, **kwargs) -> Any:
        if not self.__connection:
            self.__connection = self._connect()
        return self.__connection

    @abstractmethod
    def _connect(self, **kwargs) -> Any:
        raise NotImplementedError("connect is not implemented for this data source")

    def query(self, query, result_format="pandas", **kwargs) -> IbisTable:
        logging.info(f"Executing query: {query}")
        conn = self.connect()
        if not isinstance(conn, SQLBackend):
            raise Exception("Ibis connection is not a SQLBackend")
        result = conn.sql(query)
        if result_format == "arrow":
            result = result.to_pyarrow()
        elif result_format == "polars":
            result = result.to_polars()
        else:
            result = result.to_pandas()
        return result

    def get_catalog(
        self,
        catalog: Optional[str] = None,
    ):
        catalog = self.database if not catalog else catalog
        return self.list_schemas(catalog=catalog, with_table=True, with_columns=True)

    def list_catalogs(
        self,
        like: Optional[str] = None,
        with_schema: bool = False,
        with_table: bool = False,
        with_columns: bool = False,
    ) -> list[Catalog]:
        conn: CanListCatalog = self.connect()
        if not hasattr(conn, "list_catalogs"):
            raise Exception("This data source does not support listing catalogs")
        catalogs = [
            Catalog(catalog_name=catalog) for catalog in conn.list_catalogs(like=like)
        ]
        if with_schema:
            for catalog in catalogs:
                catalog.schemas = self.list_schemas(catalog=catalog.catalog_name)
        if with_table:
            for catalog in catalogs:
                for schema in catalog.schemas:
                    schema.tables = self.list_tables(
                        catalog=catalog.catalog_name,
                        schema=schema.schema_name,
                        with_columns=with_columns,
                    )
        return catalogs

    def list_schemas(
        self,
        catalog: Optional[str] = None,
        with_table: bool = False,
        with_columns: bool = False,
    ) -> list[Schema]:
        conn: CanListDatabase = self.connect()
        if not hasattr(conn, "list_schemas"):
            raise Exception("This data source does not support listing schemas")
        catalog = catalog or self.database or conn.current_database
        schemas = [
            Schema(schema_name=schema)
            for schema in conn.list_databases(catalog=catalog)
        ]
        if with_table:
            for schema in schemas:
                schema.tables = self.list_tables(
                    catalog=catalog,
                    schema=schema.schema_name,
                    with_columns=with_columns,
                )
        return schemas

    def list_tables(
        self,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        with_columns: bool = False,
    ) -> list[Table]:
        conn = self.connect()
        catalog = catalog or self.database or conn.current_database
        if schema is not None:
            catalog = (catalog, schema)
        tables = [
            Table(table_name=table, columns=[])
            for table in conn.list_tables(database=catalog)
        ]
        if with_columns:
            for table in tables:
                table_schema = conn.get_schema(table, catalog=catalog)
                table.columns = [
                    Column(
                        name=name,
                        type=table_schema[name].name,
                        nullable=table_schema[name].nullable,
                    )
                    for name in table_schema
                ]
        return tables

    @abstractmethod
    def get_query_plan(self, query: str) -> Any:
        raise NotImplementedError(
            "get_query_plan is not implemented for this data source."
        )

    @abstractmethod
    def crawl_metadata(self, **kwargs):
        raise NotImplementedError(
            "crawl_metadata is not implemented for this data source."
        )
