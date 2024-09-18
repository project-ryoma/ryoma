from enum import Enum

from pydantic import BaseModel

from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.bigquery import BigqueryDataSource
from ryoma_ai.datasource.file import FileDataSource
from ryoma_ai.datasource.mysql import MySqlDataSource
from ryoma_ai.datasource.nosql import DynamodbDataSource
from ryoma_ai.datasource.postgres import PostgresDataSource, PostgresConfig
from ryoma_ai.datasource.snowflake import SnowflakeDataSource, SnowflakeConfig
from ryoma_ai.datasource.sqlite import SqliteDataSource


class DataSourceProvider(Enum):
    mysql = MySqlDataSource
    postgres = PostgresDataSource
    bigquery = BigqueryDataSource
    snowflake = SnowflakeDataSource
    file = FileDataSource
    dynamodb = DynamodbDataSource
    sqlite = SqliteDataSource


class DataSourceConfigProvider(Enum):
    postgres = PostgresConfig
    snowflake = SnowflakeConfig


def get_supported_datasources():
    return list(DataSourceProvider)


class DataSourceFactory:
    @staticmethod
    def create_datasource(datasource: str,
                          *args,
                          **kwargs) -> DataSource:
        if not hasattr(DataSourceProvider, datasource):
            raise ValueError(f"Unsupported datasource: {datasource}")

        datasource_class = DataSourceProvider[datasource].value
        return datasource_class(*args, **kwargs)

    @staticmethod
    def get_model_fields(model: BaseModel):
        return model.model_fields.copy()

    @staticmethod
    def get_datasource_config(datasource: str):
        if not hasattr(DataSourceConfigProvider, datasource):
            raise ValueError(f"Unsupported datasource: {datasource}")

        config_class = DataSourceConfigProvider[datasource].value
        return DataSourceFactory.get_model_fields(config_class)
