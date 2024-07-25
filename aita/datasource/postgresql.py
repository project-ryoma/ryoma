from typing import Optional, Union

import logging

import ibis
from ibis.backends.postgres import Backend
from pydantic import Field

from aita.datasource.base import IbisDataSource
from aita.datasource.catalog import Catalog, Column, Database, Table


class PostgreSqlDataSource(IbisDataSource):
    connection_url: Optional[str] = Field(None, description="Connection URL")
    username: Optional[str] = Field(None, description="User name")
    password: Optional[str] = Field(None, description="Password")
    host: Optional[str] = Field(None, description="Host name")
    port: Optional[int] = Field(None, description="Port number")
    database: Optional[str] = Field(None, description="Database name")
    db_schema: Optional[str] = Field(None, description="Schema name")

    def connect(self) -> Backend:
        return ibis.postgres.coonect(
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            schema=self.db_schema,
        )

    def get_metadata(self, **kwargs) -> Union[Catalog, Database, Table]:
        logging.info("Getting metadata from Postgres")
        conn = self.connect()

        def get_table_metadata(database: str, schema: str) -> list[Table]:
            tables = []
            for table in conn.list_tables(database=(database, schema)):
                table_schema = conn.get_schema(table, catalog=database, database=schema)
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

        if self.database and self.db_schema:
            tables = get_table_metadata(self.database, self.db_schema)
            database = Database(database_name=self.db_schema, tables=tables)
            return database
        elif self.database:
            databases = []
            for database in conn.list_databases(catalog=self.database):
                tables = get_table_metadata(self.database, database)
                databases.append(Database(database_name=database, tables=tables))
            return Catalog(catalog_name=self.database, databases=databases)
