from abc import ABC, abstractmethod
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL as SNOW_URL


class DataSource(ABC):

    @abstractmethod
    def execute(self, query, params=None):
        pass


class SQLDataSource(DataSource):
    def __init__(self, connection_url: str):
        self.engine = create_engine(connection_url)

    def execute(self, query: str, params=None):
        with self.engine.connect() as connection:
            return connection.execute(query, *(params or ()))


class SnowflakeDataSource(SQLDataSource):
    def __init__(self, user: str, password: str, host: str, warehouse: str = "COMPUTE_WH", role: str = None, **kwargs):
        self.user = user
        self.password = password
        self.host = host
        self.warehouse = warehouse
        self.role = role
        super().__init__(self.build_connection_string())

    def build_connection_string(self) -> str:
        url = SNOW_URL(
            account=self.host,
            user=self.user,
            password=self.password,
            host=self.host,
            warehouse=self.warehouse,
            role=self.role
        )
        return url


# Implementations for various SQL databases
class MySQLDataSource(SQLDataSource):
    def __init__(self, user: str, password: str, host: str, port: str, database: str, **kwargs):
        url = URL.create("mysql+pymysql", username=user, password=password, host=host, port=port, database=database)
        super().__init__(str(url))

class PostgreSQLDataSource(SQLDataSource):
    def __init__(self, user: str, password: str, host: str, port: str, database: str, **kwargs):
        url = URL.create("postgresql", username=user, password=password, host=host, database=database)
        super().__init__(str(url))

class BigQueryDataSource(SQLDataSource):
    def __init__(self, credentials_path: str, project: str, dataset: str, **kwargs):
        url = URL.create("bigquery", credentials_path=credentials_path, project=project, dataset=dataset)
        super().__init__(str(url))


class DataSourceFactory:
    @staticmethod
    def create_datasource(**kwargs) -> DataSource:
        datasource_type = kwargs.pop("datasource")
        datasources = {
            "mysql": MySQLDataSource,
            "postgresql": PostgreSQLDataSource,
            "bigquery": BigQueryDataSource,
            "snowflake": SnowflakeDataSource,
        }

        if datasource_type not in datasources:
            raise ValueError(f"Unsupported datasource: {datasource_type}")

        return datasources[datasource_type](**kwargs)