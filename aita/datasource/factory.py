from enum import Enum

from aita.datasource.base import DataSource
from aita.datasource.bigquery import BigqueryDataSource
from aita.datasource.mysql import MySqlDataSource
from aita.datasource.postgresql import PostgreSqlDataSource
from aita.datasource.snowflake import SnowflakeDataSource
from aita.datasource.file import FileDataSource
from aita.datasource.nosql import DynamodbDataSource
from aita.datasource.sqlite import SqliteDataSource


class DataSourceProvider(Enum):
    mysql = MySqlDataSource
    postgresql = PostgreSqlDataSource
    bigquery = BigqueryDataSource
    snowflake = SnowflakeDataSource
    file = FileDataSource
    dynamodb = DynamodbDataSource
    sqlite = SqliteDataSource


def get_supported_datasources():
    return list(DataSourceProvider)


class DataSourceFactory:
    @staticmethod
    def create_datasource(datasource: str, *args, **kwargs) -> DataSource:
        if not hasattr(DataSourceProvider, datasource):
            raise ValueError(f"Unsupported datasource: {datasource}")

        datasource_class = DataSourceProvider[datasource].value
        return datasource_class(*args, **kwargs)
