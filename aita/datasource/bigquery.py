from typing import Optional, Union

import logging

import ibis
from ibis import BaseBackend, Table
from pydantic import Field

from aita.datasource.base import IbisDataSource
from aita.datasource.catalog import Catalog, Column, Database


class BigqueryDataSource(IbisDataSource):
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
