from aita.datasource.sql import SqlDataSource
import adbc_driver_postgresql.dbapi
from adbc_driver_manager.dbapi import Connection


class PostgreSqlDataSource(SqlDataSource):

    def connect(self) -> Connection:
        return adbc_driver_postgresql.dbapi.connect(self.connection_url)

