from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.engine import URL, create_engine

from aita.datasource.sql import SqlDataSource


class MySqlDataSource(SqlDataSource):

    def __init__(self,
                 connection_url: Optional[str] = None,
                 **kwargs):
        if not connection_url:
            user = kwargs.get("user")
            password = kwargs.get("password")
            host = kwargs.get("host")
            port = kwargs.get("port")
            database = kwargs.get("database")
            connection_url = self.build_connection_url(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database,
                **kwargs,
            )
        super().__init__(connection_url, "mysql")

    def build_connection_url(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        **kwargs,
    ) -> str:
        return URL(
            drivername="mysql+pymysql",
            username=user,
            password=password,
            host=host,
            port=port,
            database=database,
            query=kwargs,
        ).render_as_string()

    def connect(self) -> Engine:
        return create_engine(self.connection_url)
