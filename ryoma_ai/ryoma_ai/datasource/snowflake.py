import logging
from typing import Any, Optional, Union

import ibis
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.base_loader import Loader
from databuilder.task.task import DefaultTask
from ibis import BaseBackend
from langchain_core.pydantic_v1 import Field
from pyhocon import ConfigFactory

from ryoma_ai.datasource.base import SqlDataSource
from ryoma_ai.datasource.metadata import Catalog, Column, Database, Table


class SnowflakeDataSource(SqlDataSource):
    connection_url: Optional[str] = Field(None, description="Connection URL")
    user: Optional[str] = Field(Nscription="User name")
    password: Optional[str] = Field(None, description="Password")
    account: Optional[str] = Field(None, description="Account name")
    warehouse: Optional[str] = Field("COMPUTE_WH", description="Warehouse name")
    role: Optional[str] = Field("PUBLIC_ROLE", description="Role name")

    def connect(self, **kwargs) -> BaseBackend:
        logging.info("Connecting to Snowflake")
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
                table_schema = conn.get_schema(
                    table_name=table, catalog=database, database=schema
                )
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
        return f"snowflake://{self.user}:{self.password}@{self.account}/{self.database}/{self.db_schema}"

    def crawl_data_catalog(
        self, loader: Loader, where_clause_suffix: Optional[str] = ""
    ):
        from databuilder.extractor.snowflake_metadata_extractor import (
            SnowflakeMetadataExtractor,
        )

        logging.info("Running Snowflake metadata extraction job")
        job_config = ConfigFactory.from_dict(
            {
                "extractor.snowflake.{}".format(
                    SnowflakeMetadataExtractor.SNOWFLAKE_DATABASE_KEY
                ): self.database,
                "extractor.snowflake.{}".format(
                    SnowflakeMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY
                ): where_clause_suffix,
                "extractor.snowflake.{}".format(
                    SnowflakeMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME
                ): True,
                "extractor.snowflake.extractor.sqlalchemy.{}".format(
                    SQLAlchemyExtractor.CONN_STRING
                ): self.connection_string(),
            }
        )

        job = DefaultJob(
            conf=job_config,
            task=DefaultTask(extractor=SnowflakeMetadataExtractor(), loader=loader),
        )

        job.launch()

    def get_query_plan(self, query: str) -> Any:
        conn = self.connect()
        explain_query = f"EXPLAIN USING JSON {query}"
        return conn.sql(explain_query)
