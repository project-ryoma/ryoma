from adbc_driver_manager.dbapi import Connection
from langchain_core.pydantic_v1 import Field

from aita.datasource.sql import SqlDataSource
from typing import Optional
import adbc_driver_snowflake.dbapi


class SnowflakeDataSource(SqlDataSource):
    connection_url: str = Field(..., description="Connection URL")

    def __init__(
        self,
        connection_url: Optional[str] = None,
        **kwargs,
    ):
        if not connection_url:
            connection_url = self.build_connection_url(
                **kwargs,
            )
        super().__init__(connection_url=connection_url)

    def build_connection_url(
        self,
        user: str,
        password: str,
        account: str,
        warehouse: Optional[str] = "COMPUTE_WH",
        role: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        **kwargs,
    ) -> str:
        connection_url = f"{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}"
        if role:
            connection_url += f"&role={role}"
        if kwargs:
            connection_url += "&" + "&".join([f"{k}={v}" for k, v in kwargs.items()])
        return connection_url

    def connect(self) -> Connection:
        return adbc_driver_snowflake.dbapi.connect(self.connection_url)
