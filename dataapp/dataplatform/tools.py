from dataplatform.mysql_client import mysql_client
from dataplatform.snowflake_client import snowflake_client
from dataplatform.datasource_client import DataSourceClient
from langchain.tools import tool


@tool
def connect_to_datasource(datasource) -> DataSourceClient:
    """connect to datasource, either mysql or snowflake"""
    if datasource == "mysql":
        return mysql_client
    elif datasource == "snowflake":
        return snowflake_client
    else:
        raise ValueError("Unsupported datasource: %s" % datasource)

@tool
def preview_data(datasource: str, database: str, table: str):
    """preview data from source, currently support mysql and snowflake. need to specify database, and table name"""
    
    source_client = connect_to_datasource(datasource)
    return source_client.preview_table(database, table)


@tool
def ingest_data(source: str, destination: str, source_config: dict, destination_config: dict):
    """ingest, transport or migrate data from source to destination, currently support mysql and snowflake. need to specify database, and table name"""
    
    source_client = connect_to_datasource(source)
    destination_client = connect_to_datasource(destination)

    # ingest data from source to destination
    source_data = source_client.preview_table(source_config)
    destination_client.ingest_data(destination_config, source_data)


tools = [
    connect_to_datasource,
    preview_data,
    ingest_data,
]
