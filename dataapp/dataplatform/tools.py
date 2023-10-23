from dataplatform.mysql_client import mysql_client
from dataplatform.snowflake_client import snowflake_client
from dataplatform.datasource_client import DataSourceClient
from langchain.tools import tool, Tool
from pydantic import Field
from services.pbiembedservice import PbiEmbedService
import logging

from flask import current_app as app
import json

log = logging.getLogger(__name__)


def connect_to_datasource(datasource: str) -> DataSourceClient:
    """connect to datasource, either mysql or snowflake"""
    log.info("connect_to_datasource", datasource)
    client = None
    if datasource == "mysql":
        client = mysql_client
        return "Successfully connected to mysql"
    elif datasource == "snowflake":
        client = snowflake_client
        return "Successfully connected to snowflake"
    else:
        raise ValueError("Unsupported datasource: %s" % datasource)


def ingest_data(source: str, destination: str, source_database: str, source_table: str, destination_database: str, destination_table: str):
    """ingest, transport or migrate data from source to destination, currently support mysql and snowflake. need to specify database, and table name"""
    
    source_client = connect_to_datasource(source)
    destination_client = connect_to_datasource(destination)

    # ingest data from source to destination
    source_data = source_client.read_table_to_pandas(source_database, source_table)
    destination_client.ingest_data(source_data, destination_database, destination_table)


def create_etl(engine: str, job_type: str):
    """create etl job, there are two types of job, one is batch, another is streaming,
    for the engine, we support azure batch, airflow, spark, etc.
    """
    if not engine:
        engine = "az-batch"
    if not job_type:
        job_type = "batch"
    return


def describe_datasource(datasource: str, query: str):
    """describe datasource, get information like databases, tables, schemas, columns etc.
    example action queries:
    - show databases
    - show tables in {database}.{schema}
    - show schemas in {database}
    - show columns in {database}.{schema}.{table}
    Currently support mysql and snowflake
    """
    log.info("describe_datasource", datasource, query)
    return snowflake_client.run_query(query)

def query_datasource(datasource: str, query: str):
    """query datasource, get the analytics result, etc.
    Currently support mysql and snowflake
    Requirement:
    - For better performance, limit the number of rows returned by the query to 10 rows.
    """
    log.info("query_datasource", datasource, query)
    return snowflake_client.run_query(query)


def create_report():
    """create report, currently support powerbi, tableau, etc."""
    try:
        embed_info = PbiEmbedService().get_embed_params_for_single_report(app.config['WORKSPACE_ID'], app.config['REPORT_ID'])
        return embed_info
    except Exception as ex:
        return json.dumps({'errorMsg': str(ex)}), 500

