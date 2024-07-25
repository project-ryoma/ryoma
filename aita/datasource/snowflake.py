from typing import Optional, Union

import logging

import ibis
from ibis import BaseBackend
from ibis.backends.snowflake import Backend
from langchain_core.pydantic_v1 import Field

from aita.datasource.base import IbisDataSource
from aita.datasource.catalog import Catalog, Column, Database, Table


class SnowflakeDataSource(IbisDataSource):
    connection_url: Optional[str] = Field(None, description="Connection URL")
    user: Optional[str] = Field(Nscription="User name")
    password: Optional[str] = Field(None, description="Password")
    account: Optional[str] = Field(None, description="Account name")
    warehouse: Optional[str] = Field("COMPUTE_WH", description="Warehouse name")
    role: Optional[str] = Field("PUBLIC_ROLE", description="Role name")
    database: Optional[str] = Field(None, description="Database name")
    db_schema: Optional[str] = Field(None, description="Schema name")

    def connect(self, **kwargs) -> Union[Backend, BaseBackend]:
        logging.info("Connecting to Snowflake")
        logging.info(f"Connection URL: {self.connection_url}")
        try:
            if self.connection_url:
                logging.info("Connection URL provided, using it to connect")
                return ibis.connect(self.connection_url)
            else:
                logging.info("Connection URL not provided, using individual parameters")
                return ibis.snowflake.connect(
                    user=self.user,
                    password=self.password,
                    account=self.account,
                    warehouse=self.warehouse,
                    role=self.role,
                    database=self.database,
                    schema=self.db_schema,
                    **kwargs,
                )
        except Exception as e:
            raise Exception(f"Failed to connect to ibis: {e}")

    def get_metadata(self, **kwargs) -> Union[Catalog, Database, Table]:
        logging.info("Getting metadata from Snowflake")
        conn = self.connect()

        def get_table_metadata(database: str, schema: str) -> list[Table]:
            tables = []
            for table in conn.list_tables(database=(database, schema)):
                table_schema = conn.get_schema(table_name=table, catalog=database, database=schema)
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
