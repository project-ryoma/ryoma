from typing import Optional, Union

import ibis
from ibis import BaseBackend

from ryoma_ai.datasource.base import SqlDataSource
from ryoma_ai.datasource.metadata import Catalog, Column, Schema, Table


class SqliteDataSource(SqlDataSource):
    def __init__(self,
                 connection_url: Optional[str] = None):
        super().__init__()
        self.connection_url = connection_url

    def connect(self) -> BaseBackend:
        return ibis.sqlite.connect(self.connection_url)

    def get_metadata(self,
                     **kwargs) -> Union[Catalog, Schema, Table]:
        conn = self.connect()
        tables = []
        for table in conn.list_tables():
            table_schema = conn.get_schema(table)
            tb = Table(
                table_name=table,
                columns=[
                    Column(
                        name=name,
                        type=table_schema[name].name,
                        nullable=table_schema[name].nullable,
                    )
                    for name in table_schema
                ],
            )
            tables.append(tb)
        return Schema(
            database_name=self.connection_url,
            tables=tables,
        )

    def crawl_metadata(self,
                       **kwargs):
        pass
