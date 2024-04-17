from sqlalchemy.engine import URL

from aita.datasource.base import SqlDataSource


# Implementations for various SQL databases
class MySqlDataSource(SqlDataSource):
    def __init__(self, user: str, password: str, host: str, port: str, database: str, **kwargs):
        url = URL.create(
            "mysql+pymysql",
            username=user,
            password=password,
            host=host,
            port=port,
            database=database,
        )
        super().__init__(str(url))
