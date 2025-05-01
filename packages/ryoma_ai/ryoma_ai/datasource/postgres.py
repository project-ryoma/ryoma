import logging
from typing import Optional, Union

import ibis
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.base_loader import Loader
from databuilder.task.task import DefaultTask
from ibis import BaseBackend
from ibis.backends.sql import SQLBackend
from pydantic import BaseModel, Field
from pyhocon import ConfigFactory
from ryoma_ai.datasource.base import SqlDataSource
from ryoma_ai.datasource.metadata import Table


class PostgresConfig(BaseModel):
    user: Optional[str] = Field(None, description="Postgres user name")
    password: Optional[str] = Field(None, description="Postgres password")
    host: str = Field(..., description="Postgres host")
    port: int = Field(..., description="Postgres port")
    database: str = Field(..., description="Database name")
    db_schema: Optional[str] = Field(None, description="Database schema")


class PostgresDataSource(SqlDataSource):
    def __init__(
        self,
        user: Optional[str] = "",
        password: Optional[str] = "",
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        db_schema: Optional[str] = None,
        connection_url: Optional[str] = None,
    ):
        super().__init__(database=database, db_schema=db_schema)
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection_url = connection_url

    def _connect(self, **kwargs) -> Union[BaseBackend, SQLBackend]:
        logging.info("Connecting to Postgres")
        if self.connection_url:
            logging.info("Connection URL provided, using it to connect")
            return ibis.connect(self.connection_url, **kwargs)
        logging.info("Connection URL not provided, using individual parameters")
        conn = ibis.postgres.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            schema=self.db_schema,
            **kwargs,
        )
        logging.info("Connected to Postgres")
        return conn

    def connection_string(self):
        auth_part = (
            f"{self.user}:{self.password}@" if self.user and self.password else ""
        )
        return (
            f"postgresql+psycopg2://{auth_part}{self.host}:{self.port}/{self.database}"
        )

    def crawl_catalogs(self, loader: Loader, where_clause_suffix: Optional[str] = None):
        from databuilder.extractor.postgres_metadata_extractor import (
            PostgresMetadataExtractor,
        )

        logging.info("Start crawling metadata from Postgres database")
        job_config = ConfigFactory.from_dict(
            {
                f"extractor.postgres_metadata.st.schemaname = '{self.db_schema or 'public'}'": where_clause_suffix,
                PostgresMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME: True,
                f"extractor.postgres_metadata.extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}": self.connection_string(),
            }
        )
        job = DefaultJob(
            conf=job_config,
            task=DefaultTask(extractor=PostgresMetadataExtractor(), loader=loader),
        )
        job.launch()

    def get_query_plan(self, query: str) -> Table:
        conn = self.connect()
        explain_query = f"EXPLAIN {query}"
        return conn.sql(explain_query)
