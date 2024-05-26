from abc import abstractmethod
from typing import Any, Optional

from pydantic import Field

from aita.datasource.catalog import Catalog
from aita.datasource.base import DataSource
import pyarrow as pa


class SqlDataSource(DataSource):
    type: str = "sql"

    @abstractmethod
    def connect(self) -> Any:
        raise NotImplementedError

    def execute(self, query: str, params=None):
        with self.connect().cursor() as cursor:
            cursor.execute(query, *(params or ()))
            return cursor.fetchall()

    def get_metadata(self, **kwargs) -> Catalog:
        with self.connect() as conn:
            catalogs: pa.Table = conn.adbc_get_objects(
                catalog_filter=kwargs.get("database", conn.adbc_current_catalog),
                db_schema_filter=kwargs.get("schema", conn.adbc_current_db_schema),
                table_name_filter=kwargs.get("table", None),
            ).read_all()
            catalog = catalogs.to_pylist()[0]
            return Catalog(**catalog)

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
