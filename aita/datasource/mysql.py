from typing import Optional, Union

import logging

import ibis
from ibis import BaseBackend
from pydantic import Field

from aita.datasource.base import IbisDataSource
from aita.datasource.catalog import Catalog, Column, Database, Table


class MySqlDataSource(IbisDataSource):
    connection_url: Optional[str] = Field(None, description="Connection URL")
    username: Optional[str] = Field(None, description="User name")
    password: Optional[str] = Field(None, description="Password")
    host: Optional[str] = Field(None, description="Host name")
    port: Optional[int] = Field(None, description="Port number")
    database: Optional[str] = Field(None, description="Database name")

    def connect(self, **kwargs) -> BaseBackend:
        return ibis.mysql.coonect(
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            **kwargs,
        )

    def get_metadata(self, **kwargs) -> Union[Catalog, Database, Table]:
        logging.info("Getting metadata from Mysql")
        conn = self.connect()

        def get_table_metadata(database: str) -> list[Table]:
            tables = []
            for table in conn.list_tables(database=database):
                table_schema = conn.get_schema(table, database=database)
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
            return tables

        tables = get_table_metadata(self.database)
        return Database(database_name=self.database, tables=tables)
