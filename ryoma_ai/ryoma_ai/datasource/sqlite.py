
import ibis
from ibis import BaseBackend
from pydantic import BaseModel, Field

from ryoma_ai.datasource.base import SqlDataSource


class SqliteConfig(BaseModel):
    connection_url: str = Field(..., description="Sqlite connection URL")


class SqliteDataSource(SqlDataSource):
    def __init__(self,
                 connection_url: str):
        super().__init__()
        self.connection_url = connection_url

    def connect(self) -> BaseBackend:
        return ibis.sqlite.connect(self.connection_url)
