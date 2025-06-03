import logging
from typing import Optional

import ibis
from databuilder.job.job import DefaultJob
from databuilder.loader.base_loader import Loader
from databuilder.task.task import DefaultTask
from ibis import BaseBackend
from langchain_core.pydantic_v1 import Field
from pyhocon import ConfigFactory
from ryoma_ai.datasource.sql import SqlDataSource


class BigqueryDataSource(SqlDataSource):
    project_id: str = Field(..., description="Bigquery current_store ID")
    dataset_id: str = Field(..., description="Bigquery dataset ID")
    credentials: Optional[str] = Field(None, description="Path to the credentials file")

    def _connect(self, **kwargs) -> BaseBackend:
        return ibis.bigquery.connect(
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            credentials=self.credentials,
            **kwargs,
        )

    def crawl_catalog(self, loader: Loader, where_clause_suffix: Optional[str] = ""):
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
