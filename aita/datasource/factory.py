from aita.datasource.base import DataSource
from aita.datasource.bigquery import BigQueryDataSource
from aita.datasource.mysql import MySqlDataSource
from aita.datasource.postgresql import PostgreSqlDataSource
from aita.datasource.snowflake import SnowflakeDataSource


class DataSourceFactory:
    @staticmethod
    def create_datasource(**kwargs) -> DataSource:
        datasource_type = kwargs.pop("datasource")
        datasources = {
            "mysql": MySqlDataSource,
            "postgresql": PostgreSqlDataSource,
            "bigquery": BigQueryDataSource,
            "snowflake": SnowflakeDataSource,
        }

        if datasource_type not in datasources:
            raise ValueError(f"Unsupported datasource: {datasource_type}")

        return datasources[datasource_type](**kwargs)
