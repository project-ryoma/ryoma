from adbc_driver_manager.dbapi import Connection
from sqlalchemy.engine import URL

from aita.datasource.sql import SqlDataSource


class BigqueryDataSource(SqlDataSource):
    def connect(self) -> Connection:
        pass

    def __init__(self, credentials_path: str, project: str, dataset: str, **kwargs):
        url = URL.create(
            "bigquery", credentials_path=credentials_path, project=project, dataset=dataset
        )
        super().__init__(str(url))
