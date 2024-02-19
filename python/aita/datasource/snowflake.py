from snowflake.sqlalchemy import URL
from aita.datasource.base import SQLDataSource


class SnowflakeDataSource(SQLDataSource):
    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        warehouse: str = "COMPUTE_WH",
        role: str = None,
        **kwargs,
    ):
        self.user = user
        self.password = password
        self.host = host
        self.warehouse = warehouse
        self.role = role
        super().__init__(self.build_connection_string())

    def build_connection_string(self) -> str:
        url = URL(
            account=self.host,
            user=self.user,
            password=self.password,
            host=self.host,
            warehouse=self.warehouse,
            role=self.role,
        )
        return url
