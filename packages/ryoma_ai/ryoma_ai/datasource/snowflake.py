import logging
from typing import Any, Optional, Union

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
from ryoma_ai.datasource.metadata import Catalog, Column, Schema, Table


class SnowflakeConfig(BaseModel):
    user: str = Field(..., description="Snowflake user name")
    password: str = Field(..., description="Snowflake password")
    account: str = Field(..., description="Snowflake account")
    database: str = Field(..., description="Database name")
    warehouse: Optional[str] = Field(None, description="Snowflake warehouse name")
    role: Optional[str] = Field(None, description="Snowflake role name")
    db_schema: Optional[str] = Field(None, description="Database schema")


class SnowflakeDataSource(SqlDataSource):
    def __init__(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
        account: Optional[str] = None,
        database: Optional[str] = None,
        warehouse: Optional[str] = None,
        role: Optional[str] = None,
        db_schema: Optional[str] = None,
        connection_url: Optional[str] = None,
    ):
        super().__init__(database=database, db_schema=db_schema)
        self.user = user
        self.password = password
        self.account = account
        self.warehouse = warehouse or "COMPUTE_WH"
        self.role = role or "PUBLIC_ROLE"
        self.connection_url = connection_url

    def _connect(self, **kwargs) -> Union[BaseBackend, SQLBackend]:
        if self.connection_url:
            logging.info("Connection URL provided, using it to connect")
            return ibis.connect(self.connection_url)
        logging.info("Connection URL not provided, using individual parameters")
        try:
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
            raise Exception(f"Failed to connect to Snowflake: {e}")

    def connection_string(self):
        return """
        snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}
        """.format(
            user=self.user,
            password=self.password,
            account=self.account,
            database=self.database,
            schema=self.db_schema,
            warehouse=self.warehouse,
            role=self.role,
        )

    def crawl_catalogs(self, loader: Loader, where_clause_suffix: Optional[str] = ""):
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
