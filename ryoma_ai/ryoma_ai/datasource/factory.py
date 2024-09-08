from enum import Enum

from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.bigquery import BigqueryDataSource
from ryoma_ai.datasource.file import FileDataSource
from ryoma_ai.datasource.mysql import MySqlDataSource
from ryoma_ai.datasource.nosql import DynamodbDataSource
from ryoma_ai.datasource.postgresql import PostgreSqlDataSource
from ryoma_ai.datasource.snowflake import SnowflakeDataSource
from ryoma_ai.datasource.sqlite import SqliteDataSource


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
