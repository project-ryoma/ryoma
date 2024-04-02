from sqlalchemy.engine.url import URL

from aita.datasource.base import SqlDataSource


class PostgreSqlDataSource(SqlDataSource):
    def __init__(self, user: str, password: str, host: str, port: str, database: str, **kwargs):
        url = URL.create(
            "postgresql", username=user, password=password, host=host, database=database
        )
        super().__init__(str(url))
