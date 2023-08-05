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
def ingest_data(source: str, destination: str, source_database: str, source_table, destination_database: str, destination_table: str):
    """ingest, transport or migrate data from source to destination, currently support mysql and snowflake. need to specify database, and table name"""
    
    source_client = connect_to_datasource(source)
    destination_client = connect_to_datasource(destination)

    # ingest data from source to destination
    source_data = source_client.read_table_to_pandas(source_database, source_table)
    destination_client.ingest_data(source_data, destination_database, destination_table)


@tool
def create_etl(engine: str, job_type: str):
    """create etl job, there are two types of job, one is batch, another is streaming,
    for the engine, we support azure batch, airflow, spark, etc.
    """
    if not engine:
        engine = "az-batch"
    if not job_type:
        job_type = "batch"
    

tools = [
    connect_to_datasource,
    preview_data,
    ingest_data,
    create_etl
]
