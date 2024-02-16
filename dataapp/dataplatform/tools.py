from sqlalchemy import create_engine
from services.pbiembedservice import PbiEmbedService
from dataplatform import DataSourceFactory
import logging

from flask import current_app as app
import json

log = logging.getLogger(__name__)

states_store = {}


def connect_to_datasource(datasource: str, **configs):
    """connect to datasource, either mysql or snowflake"""
    log.info("connect_to_datasource", datasource)
    try:
        datasource = DataSourceFactory.create_datasource(datasource=datasource, **configs)
        states_store['db'] = datasource

        return datasource
    except KeyError:
        raise ValueError(f"Unsupported datasource: {datasource}")


def ingest_data(source: str, destination: str, source_database: str, source_table: str, destination_database: str,
                destination_table: str):
    """ingest, transport or migrate data from source to destination, currently support mysql and snowflake. need to specify database, and table name"""

    source_client = connect_to_datasource(source)
    destination_client = connect_to_datasource(destination)

    # ingest data from source to destination
    source_data = source_client.read_table_to_pandas(source_database, source_table)
    destination_client.ingest_data(source_data, destination_database, destination_table)


def query_datasource(datasource: str, query: str):
    """query datasource, get the analytics result, etc.
    Currently, support mysql and snowflake
    Requirement:
    - For better performance, limit the number of rows returned by the query to 10 rows.
    """
    log.info("query_datasource", datasource, query)
    conn = states_store['db']
    res = conn.execute(query).fetchall()
    json_result = [dict(r) for r in res]
    return json_result


def create_report():
    """create report, currently support powerbi, tableau, etc."""
    try:
        embed_info = PbiEmbedService().get_embed_params_for_single_report(app.config['WORKSPACE_ID'],
                                                                          app.config['REPORT_ID'])
        return embed_info
    except Exception as ex:
        return json.dumps({'errorMsg': str(ex)}), 500
