from typing import Any

from abc import abstractmethod

import pyarrow as pa

from aita.datasource.base import DataSource
from aita.datasource.catalog import Catalog


class SqlDataSource(DataSource):
    type: str = "sql"

    @abstractmethod
    def connect(self) -> Any:
        raise NotImplementedError

    def execute(self, query: str, params=None):
        with self.connect().cursor() as cursor:
            cursor.execute(query, *(params or ()))
            return cursor.fetchall()
    @abstractmethod
    def get_metadata(self, **kwargs) -> Catalog:
        raise NotImplementedError

    def to_arrow(self, query: str, params=None):
        with self.connect().cursor() as cursor:
            cursor.execute(query, *(params or ()))
            return cursor.fetch_arrow_table()

    def to_pandas(self, query: str, params=None):
        return self.to_arrow(query, params).to_pandas()

    def ingest(self, table_name: str, data: pa.Table, **kwargs):
        with self.connect().cursor() as cursor:
            res = cursor.adbc_ingest(table_name, data, **kwargs)
            cursor.connection.commit()
            return res
