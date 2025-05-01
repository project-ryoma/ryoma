import inspect
from typing import Any, Optional

import duckdb
from ryoma_ai.datasource.base import SqlDataSource


class DuckDBConfig:
    database: Optional[str] = ":memory:"
    read_only: Optional[bool] = False
    temp_directory: Optional[str] = None
    extensions: Optional[list] = None
    config: Optional[dict] = None


class DuckDBDataSource(SqlDataSource):

    def get_query_plan(self, query: str) -> Any:
        pass

    def crawl_catalogs(self, **kwargs):
        pass

    def __init__(
        self,
        database: str = ":memory:",
        read_only: bool = False,
        temp_directory: Optional[str] = None,
        extensions: Optional[list] = None,
        config: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(database=database, **kwargs)
        self.read_only = read_only
        self.config = config or {}
        if temp_directory:
            self.config["temp_directory"] = temp_directory
        self.extensions = extensions

    def _connect(self, **kwargs) -> Any:
        conn = duckdb.connect(
            database=self.database,
            read_only=self.read_only,
            config=self.config,
        )
        if self.extensions:
            for extension in self.extensions:
                conn.load_extension(extension)
        return conn

    def query(self, query, result_format="pandas", **kwargs) -> Any:
        conn = self.connect()
        # TODO: Should we abstract this to support other backends?
        inspect.currentframe().f_locals.update(**kwargs)
        return conn.sql(query).execute().fetchdf()

    def register(self, name: str, data: Any, **kwargs):
        conn = self.connect()
        conn.register(name, data)
