from typing import Optional, Union

import ibis
from ibis import BaseBackend
from pydantic import Field

from aita.datasource.base import IbisDataSource
from aita.datasource.metadata import Catalog, Column, Database, Table


class SqliteDataSource(IbisDataSource):
    connection_url: str = Field(..., description="Connection URL")

    def __init__(
        self,
        connection_url: Optional[str] = None,
    ):
        super().__init__(connection_url=connection_url)

    def connect(self) -> BaseBackend:
        return ibis.sqlite.connect(self.connection_url)

    def get_metadata(self, **kwargs) -> Union[Catalog, Database, Table]:
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
        return Database(
            database_name=self.connection_url,
            tables=tables,
        )
