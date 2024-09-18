from enum import Enum

from pydantic import BaseModel

from ryoma_ai.datasource.base import DataSource
from ryoma_ai.datasource.bigquery import BigqueryDataSource
from ryoma_ai.datasource.file import FileDataSource
from ryoma_ai.datasource.mysql import MySqlDataSource
from ryoma_ai.datasource.nosql import DynamodbDataSource
from ryoma_ai.datasource.postgresql import PostgresDataSource
from ryoma_ai.datasource.snowflake import SnowflakeDataSource
from ryoma_ai.datasource.sqlite import SqliteDataSource


class DataSourceProvider(Enum):
    mysql = MySqlDataSource
    postgresql = PostgresDataSource
    bigquery = BigqueryDataSource
    snowflake = SnowflakeDataSource
    file = FileDataSource
    dynamodb = DynamodbDataSource
    sqlite = SqliteDataSource


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
        if datasource == "postgresql":
            from feast.infra.online_stores.contrib.postgres import PostgreSQLOnlineStoreConfig
            return DataSourceFactory.get_model_fields(PostgreSQLOnlineStoreConfig)
        if datasource == "snowflake":
            from feast.infra.online_stores.snowflake import SnowflakeOnlineStoreConfig
            return DataSourceFactory.get_model_fields(SnowflakeOnlineStoreConfig)

