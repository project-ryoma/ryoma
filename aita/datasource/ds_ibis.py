from typing import Optional

import ibis
from ibis import BaseBackend, Table
from ibis.backends.sql import SQLBackend
from pydantic import Field

from aita.datasource.base import DataSource


class IbisDataSource(DataSource):
    type: str = "ibis"
    connection_url: Optional[str] = Field(None, description="Connection URL")

    def connect(self, **kwargs) -> BaseBackend:
        try:
            return ibis.connect(self.connection_url, **kwargs)
        except Exception as e:
            raise Exception(f"Failed to connect to ibis: {e}")

    def execute(self, query, result_format="pandas", **kwargs) -> Table:
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

    def get_metadata(self, **kwargs):
        return self.connection.list_databases()
