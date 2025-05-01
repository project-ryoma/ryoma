from typing import Any

import ibis
from ibis import BaseBackend
from pydantic import BaseModel, Field
from ryoma_ai.datasource.base import SqlDataSource


class SqliteConfig(BaseModel):
    connection_url: str = Field(..., description="Sqlite connection URL")


class SqliteDataSource(SqlDataSource):
    def get_query_plan(self, query: str) -> Any:
        pass

    def crawl_catalogs(self, **kwargs):
        pass

    def __init__(self, connection_url: str):
        super().__init__()
        self.connection_url = connection_url

    def _connect(self) -> BaseBackend:
        return ibis.sqlite.connect(self.connection_url)
