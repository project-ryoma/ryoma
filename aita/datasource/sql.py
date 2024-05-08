from abc import abstractmethod
from adbc_driver_manager.dbapi import Connection
from aita.datasource.catalog import Catalog
from aita.datasource.base import DataSource
from typing import List
import json
import pyarrow as pa
from pyarrow.csv import read_csv


class SqlDataSource(DataSource):
    def __init__(self, connection_url: str):
        self.connection_url = connection_url

    @abstractmethod
    def connect(self) -> Connection:
        raise NotImplementedError

    def execute(self, query: str, params=None):
        with self.connect().cursor() as cursor:
            cursor.execute(query, *(params or ()))
            return cursor.fetchall()

    def get_metadata(self, **kwargs) -> List[Catalog]:
        with self.connect() as conn:
            catalogs: pa.Table = conn.adbc_get_objects(
                catalog_filter=kwargs.get("database", conn.adbc_current_catalog),
                db_schema_filter=kwargs.get("schema", conn.adbc_current_db_schema),
                table_name_filter=kwargs.get("table"),
            ).read_all()
            catalog_list = json.loads(catalogs.to_pandas().to_json(orient="records"))
            return [Catalog(**catalog) for catalog in catalog_list]

    def to_arrow(self, query: str, params=None):
        with self.connect().cursor() as cursor:
            cursor.execute(query, *(params or ()))
            return cursor.fetch_arrow_table()

    def to_pandas(self, query: str, params=None):
        return self.to_arrow(query, params).to_pandas()

    def ingest(self, table_name: str, data: pa.Table, **kwargs):
        with self.connect().cursor() as cursor:
            print(cursor.adbc_ingest(table_name, data, **kwargs))
            cursor.close()
