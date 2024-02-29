from sqlalchemy.engine import URL

from aita.datasource.base import SqlDataSource


class BigQueryDataSource(SqlDataSource):
    def __init__(self, credentials_path: str, project: str, dataset: str, **kwargs):
        url = URL.create(
            "bigquery", credentials_path=credentials_path, project=project, dataset=dataset
        )
        super().__init__(str(url))
