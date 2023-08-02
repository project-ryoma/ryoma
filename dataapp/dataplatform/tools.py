from dataplatform.mysql_client import mysql_client
from dataplatform.snowflake_client import snowflake_client
from langchain.agents import Tool
from langchain.tools import tool
from pydantic import BaseModel


@tool
def connect_to_datasource(datasource):
    """connect to source database"""
    if datasource == "mysql":
        return mysql_client
    elif datasource == "snowflake":
        return snowflake_client
    else:
        raise ValueError("Unsupported datasource: %s" % datasource)


def run_query_on_mysql(sql_query):
    return mysql_client.run_query(sql_query)


def preview_data_on_mysql(database, table):
    return mysql_client.preview_table(database, table)


def run_query_on_snowflake(sql_query):
    return snowflake_client.run_query(sql_query)


@tool
def preview_data_on_snowflake(database, scheme, table):
    """preview data on snowflake, need to specify database, schema and table/view name"""
    return snowflake_client.preview_table(database, scheme, table)


@tool
def ingest_data_from_source_to_destination(source, destination):
    """ingest data from source to destination"""

    source_client = connect_to_datasource(source)
    destination_client = connect_to_datasource(destination)
    return


tools = [
    connect_to_datasource,
    Tool(
        name="run_query_on_mysql",
        func=run_query_on_mysql,
        description="run query on mysql database"
    ),
    Tool(
        name="run_query_on_snowflake",
        func=run_query_on_snowflake,
        description="run query on snowflake database"
    ),
    Tool(
        name="preview_data_on_mysql",
        func=preview_data_on_mysql,
        description="preview data on mysql, need to specify database, and table name"
    ),
    preview_data_on_snowflake,
    ingest_data_from_source_to_destination
]
