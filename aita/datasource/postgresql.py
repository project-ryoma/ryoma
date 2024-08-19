from typing import Optional, Union

import logging

import ibis
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.base_loader import Loader
from databuilder.task.task import DefaultTask
from ibis import BaseBackend
from langchain_core.pydantic_v1 import Field
from pyhocon import ConfigFactory

from aita.datasource.base import SqlDataSource
from aita.datasource.metadata import Catalog, Column, Database, Table


class PostgreSqlDataSource(SqlDataSource):
    connection_url: Optional[str] = Field(None, description="Connection URL")
    username: Optional[str] = Field(None, description="User name")
    password: Optional[str] = Field(None, description="Password")
    host: Optional[str] = Field(None, description="Host name")
    port: Optional[int] = Field(None, description="Port number")
    database: Optional[str] = Field(None, description="Database name")
    db_schema: Optional[str] = Field(None, description="Schema name")

    def connect(self) -> BaseBackend:
        logging.info("Connecting to Postgres")
        if self.connection_url is not None:
            logging.info("Connection URL provided, using it to connect")
            return ibis.connect(self.connection_url)
        else:
            logging.info("Connection URL not provided, using individual parameters")
            return ibis.postgres.connect(
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

    def connection_string(self):
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}/{self.db_schema}"

    def crawl_data_catalog(self, loader: Loader, where_clause_suffix: Optional[str] = ""):
        from databuilder.extractor.postgres_metadata_extractor import PostgresMetadataExtractor

        logging.info("Started crawling data catalog from Postgres")
        job_config = ConfigFactory.from_dict(
            {
                "extractor.postgres_metadata.{}".format(
                    PostgresMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY
                ): where_clause_suffix,
                "extractor.postgres_metadata.{}".format(
                    PostgresMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME
                ): True,
                "extractor.postgres_metadata.extractor.sqlalchemy.{}".format(
                    SQLAlchemyExtractor.CONN_STRING
                ): self.connection_string(),
            }
        )
        job = DefaultJob(
            conf=job_config, task=DefaultTask(extractor=PostgresMetadataExtractor(), loader=loader)
        )
        job.launch()

    def get_query_plan(self, query: str) -> str:
        conn = self.connect()
        explain_query = f"EXPLAIN {query}"
        return conn.sql(explain_query)
