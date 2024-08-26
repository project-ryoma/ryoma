import logging
from typing import Optional, Union

import ibis
from databuilder.job.job import DefaultJob
from databuilder.loader.base_loader import Loader
from databuilder.task.task import DefaultTask
from ibis import BaseBackend, Table
from langchain_core.pydantic_v1 import Field
from pyhocon import ConfigFactory

from ryoma.datasource.base import SqlDataSource
from ryoma.datasource.metadata import Catalog, Column, Database


class BigqueryDataSource(SqlDataSource):
    project_id: str = Field(..., description="Bigquery project ID")
    dataset_id: str = Field(..., description="Bigquery dataset ID")
    credentials: Optional[str] = Field(None, description="Path to the credentials file")

    def connect(self, **kwargs) -> BaseBackend:
        return ibis.bigquery.connect(
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            credentials=self.credentials,
            **kwargs,
        )

    def get_metadata(self, **kwargs) -> Union[Catalog, Database, Table]:
        logging.info("Getting metadata from Bigquery")
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
        return Database(database_name=self.dataset_id, tables=tables)

    def crawl_data_catalog(
        self, loader: Loader, where_clause_suffix: Optional[str] = ""
    ):
        from databuilder.extractor.bigquery_metadata_extractor import (
            BigQueryMetadataExtractor,
        )

        logging.info("Crawling data catalog from Bigquery")
        job_config = ConfigFactory.from_dict(
            {
                "extractor.bigquery_table_metadata.{}".format(
                    BigQueryMetadataExtractor.PROJECT_ID_KEY
                )
            }
        )
        job = DefaultJob(
            conf=job_config,
            task=DefaultTask(extractor=BigQueryMetadataExtractor(), loader=loader),
        )

        job.launch()
