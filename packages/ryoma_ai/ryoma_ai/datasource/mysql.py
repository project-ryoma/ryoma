import logging
from typing import Any, Optional, Union

import ibis
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.base_loader import Loader
from databuilder.task.task import DefaultTask
from ibis import BaseBackend
from pyhocon import ConfigFactory
from ryoma_ai.datasource.base import SqlDataSource


class MySqlDataSource(SqlDataSource):
    def get_query_plan(self, query: str) -> Any:
        pass

    def __init__(
        self,
        database: Optional[str] = None,
        db_schema: Optional[str] = None,
        connection_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        super().__init__(database=database, db_schema=db_schema)
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.connection_url = connection_url

    def _connect(self, **kwargs) -> BaseBackend:
        return ibis.mysql.connect(
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            **kwargs,
        )

    def connection_string(self):
        return f"mysql+mysqlconnector://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def crawl_catalogs(self, loader: Loader, where_clause_suffix: Optional[str] = ""):
        from databuilder.extractor.mysql_metadata_extractor import (
            MysqlMetadataExtractor,
        )

        logging.info("Crawling data catalog from Mysql")
        job_config = ConfigFactory.from_dict(
            {
                "extractor.mysql_metadata.{}".format(
                    MysqlMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY
                ): where_clause_suffix,
                "extractor.mysql_metadata.{}".format(
                    MysqlMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME
                ): True,
                "extractor.mysql_metadata.extractor.sqlalchemy.{}".format(
                    SQLAlchemyExtractor.CONN_STRING
                ): self.connection_string(),
            }
        )
        job = DefaultJob(
            conf=job_config,
            task=DefaultTask(extractor=MysqlMetadataExtractor(), loader=loader),
        )
        job.launch()


class MySqlConfig:
    pass
