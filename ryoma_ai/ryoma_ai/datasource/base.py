import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Union

import ibis
from ibis import Table as IbisTable
from ibis.backends import CanListCatalog, CanListDatabase
from ibis.backends.sql import SQLBackend
from langchain_core.pydantic_v1 import BaseModel
from pydantic import Field

from ryoma_ai.datasource.metadata import Catalog, Schema, Table


class DataSource(BaseModel, ABC):
    type: str = Field(..., description="Type of the data source")

    @abstractmethod
    def crawl_metadata(self, **kwargs):
        raise NotImplementedError(
            "crawl_metadata is not implemented for this data source"
        )


class SqlDataSource(DataSource):
    type: str = "ibis"
    database: Optional[str] = Field(None, description="Schema name")
    db_schema: Optional[str] = Field(None, description="Schema name")
    connection_url: Optional[str] = Field(None, description="Connection URL")

    def connect(self, **kwargs) -> SQLBackend:
        logging.info("Connecting to ibis data source")
        try:
            return ibis.connect(self.connection_url, **kwargs)
        except Exception as e:
            raise Exception(f"Failed to connect to ibis: {e}")

    def query(self, query, result_format="pandas", **kwargs) -> IbisTable:
        logging.info("Executing query: {}".format(query))
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

    def list_catalogs(
        self,
        like: Optional[str] = None,
        with_schema: bool = False,
        with_table: bool = False,
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
                        catalog=catalog.catalog_name, schema=schema.schema_name
                    )
        return catalogs

    def list_schemas(
        self, catalog: Optional[str] = None, with_table: bool = False
    ) -> list[Schema]:
        conn: CanListDatabase = self.connect()
        if not hasattr(conn, "list_schemas"):
            raise Exception("This data source does not support listing schemas")
        if not catalog:
            catalog = self.database
        schemas = [
            Schema(schema_name=schema)
            for schema in conn.list_databases(catalog=catalog)
        ]
        if with_table:
            for schema in schemas:
                schema.tables = self.list_tables(
                    catalog=catalog, schema=schema.schema_name
                )
        return schemas

    def list_tables(
        self, catalog: Optional[str] = None, schema: Optional[str] = None
    ) -> list[Table]:
        conn = self.connect()
        catalog = self.database if not catalog else catalog
        if schema is not None:
            catalog = (catalog, schema)
        tables = conn.list_tables(database=catalog)
        return [Table(table_name=table, columns=[]) for table in tables]

    @abstractmethod
    def get_query_plan(self, query: str) -> Any:
        raise NotImplementedError(
            "get_query_plan is not implemented for this data source."
        )

    @abstractmethod
    def get_metadata(self, **kwargs) -> Union[Catalog, Schema, Table]:
        pass
