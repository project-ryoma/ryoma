from enum import Enum

from pydantic import BaseModel
from ryoma_ai.datasource.base import DataSource, SqlDataSource
from ryoma_ai.datasource.bigquery import BigqueryDataSource
from ryoma_ai.datasource.duckdb import DuckDBConfig, DuckDBDataSource
from ryoma_ai.datasource.file import FileConfig, FileDataSource
from ryoma_ai.datasource.mysql import MySqlConfig, MySqlDataSource
from ryoma_ai.datasource.nosql import DynamodbConfig, DynamodbDataSource
from ryoma_ai.datasource.postgres import PostgresConfig, PostgresDataSource
from ryoma_ai.datasource.snowflake import SnowflakeConfig, SnowflakeDataSource
from ryoma_ai.datasource.sqlite import SqliteConfig, SqliteDataSource


class DataSourceProvider(Enum):
    mysql = MySqlDataSource
    postgres = PostgresDataSource
    bigquery = BigqueryDataSource
    snowflake = SnowflakeDataSource
    file = FileDataSource
    dynamodb = DynamodbDataSource
    sqlite = SqliteDataSource
    duckdb = DuckDBDataSource


class DataSourceConfigProvider(Enum):
    postgres = PostgresConfig
    snowflake = SnowflakeConfig
    file = FileConfig
    mysql = MySqlConfig
    dynamodb = DynamodbConfig
    sqlite = SqliteConfig
    duckdb = DuckDBConfig


def get_supported_datasources():
    return list(DataSourceProvider)


class DataSourceFactory:
    @staticmethod
    def create_datasource(datasource: str, *args, **kwargs) -> SqlDataSource:
        if not hasattr(DataSourceProvider, datasource):
            raise ValueError(f"Unsupported datasource: {datasource}")

        datasource_class = DataSourceProvider[datasource].value
        return datasource_class(*args, **kwargs)

    @staticmethod
    def get_model_fields(model: BaseModel):
        return model.model_fields.copy()

    @staticmethod
    def get_datasource_config(datasource: str):
        if not hasattr(DataSourceProvider, datasource):
            raise ValueError(f"Unsupported datasource: {datasource}")

        config_class = DataSourceConfigProvider[datasource].value
        return DataSourceFactory.get_model_fields(config_class)
