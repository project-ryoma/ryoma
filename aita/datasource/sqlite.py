from typing import Optional

import adbc_driver_sqlite.dbapi
import pyarrow as pa
from adbc_driver_manager.dbapi import Connection
from pydantic import Field

from aita.datasource.catalog import Catalog
from aita.datasource.sql import SqlDataSource


class SqliteDataSource(SqlDataSource):
    connection_url: str = Field(..., description="Connection URL")

    def __init__(
        self,
        connection_url: Optional[str] = None,
    ):
        super().__init__(connection_url=connection_url)

    def connect(self) -> Connection:
        return adbc_driver_sqlite.dbapi.connect(self.connection_url)

    def get_metadata(self, **kwargs) -> Catalog:
        with self.connect() as conn:

            catalogs: pa.Table = conn.adbc_get_objects(
                catalog_filter=kwargs.get("database", conn.adbc_current_catalog),
                table_name_filter=kwargs.get("table", None),
            ).read_all()
            catalog = catalogs.to_pylist()[0]
            return Catalog(**catalog)
