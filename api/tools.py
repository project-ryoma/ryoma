import logging
from function_calls import openai_function
from metadb import state_store

log = logging.getLogger(__name__)


@openai_function
def query_datasource(datasource: str, query: str):
    """query datasource, get the analytics result, etc.
    Currently, support mysql and snowflake
    Requirement:
    - For better performance, limit the number of rows returned by the query to 10 rows.
    """
    print("query_datasource", datasource, query, state_store.cache)
    conn = state_store.cache[datasource]
    print(conn)
    return conn.execute(query).fetchall()
    # json_result = [dict(r) for r in res]
    # return json_result


tool_schemas = [
    query_datasource.openai_schema
]