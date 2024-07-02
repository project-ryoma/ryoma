from typing import Optional

import pyarrow as pa

try:
    import adbc_driver_postgresql.dbapi
except ImportError:
    adbc_driver_postgresql = None
from adbc_driver_manager.dbapi import Connection
from pydantic import Field

from aita.datasource.catalog import Catalog
from aita.datasource.sql import SqlDataSource


class PostgreSqlDataSource(SqlDataSource):
    connection_url: str = Field(..., description="Connection URL")

    def __init__(
        self,
        connection_url: Optional[str] = None,
        **kwargs,
    ):
        if not connection_url:
            user = kwargs.get("user")
            password = kwargs.get("password")
            host = kwargs.get("host")
            port = kwargs.get("port")
            database = kwargs.get("database")
            connection_url = self.build_connection_url(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database,
                **kwargs,
            )
        super().__init__(connection_url=connection_url)

    def build_connection_url(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        **kwargs,
    ) -> str:
        connection_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        if kwargs:
            connection_url += "?" + "&".join([f"{k}={v}" for k, v in kwargs.items()])
        return connection_url

    def connect(self) -> Connection:
        return adbc_driver_postgresql.dbapi.connect(self.connection_url)

    def get_metadata(self, **kwargs):
        with self.connect() as conn:
            catalogs: pa.Table = conn.adbc_get_objects(
                catalog_filter=kwargs.get("database", conn.adbc_current_catalog),
                db_schema_filter=kwargs.get("feature", conn.adbc_current_db_schema),
                table_name_filter=kwargs.get("table", None),
            ).read_all()
            catalog = catalogs.to_pylist()[0]
            return Catalog(**catalog)
