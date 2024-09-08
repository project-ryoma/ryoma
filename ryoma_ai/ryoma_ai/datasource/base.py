import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Union

import ibis
from ibis import BaseBackend, Table
from ibis.backends.sql import SQLBackend
from langchain_core.pydantic_v1 import BaseModel
from pydantic import Field

from ryoma_ai.datasource.metadata import Catalog, Database


class DataSource(BaseModel, ABC):
    type: str = Field(..., description="Type of the data source")


class SqlDataSource(DataSource):
    type: str = "ibis"
    database: Optional[str] = Field(None, description="Database name")
    db_schema: Optional[str] = Field(None, description="Schema name")
    connection_url: Optional[str] = Field(None, description="Connection URL")

    def connect(self, **kwargs) -> BaseBackend:
        logging.info("Connecting to ibis data source")
        try:
            return ibis.connect(self.connection_url, **kwargs)
        except Exception as e:
            raise Exception(f"Failed to connect to ibis: {e}")

    def query(self, query, result_format="pandas", **kwargs) -> Table:
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

    @abstractmethod
    def get_query_plan(self, query: str) -> Any:
        raise NotImplementedError(
            "get_query_plan is not implemented for this data source."
        )

    @abstractmethod
    def get_metadata(self, **kwargs) -> Union[Catalog, Database, Table]:
        pass

    @abstractmethod
    def crawl_data_catalog(self, **kwargs):
        raise NotImplementedError(
            "crawl_data_catalog is not implemented for this data source"
        )
