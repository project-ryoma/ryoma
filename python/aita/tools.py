from typing import Any

import logging

from aita.function_calls import openai_function
from aita.metadb import state_store

log = logging.getLogger(__name__)


@openai_function
def query_datasource(datasource: str, query: str) -> Any:
    """query datasource, get the analytics result, etc.
    Currently, support mysql and snowflake
    Requirement:
    - For better performance, limit the number of rows returned by the query to 10 rows.
    """
    conn = state_store.cache[datasource]
    query_result = conn.execute(query).fetchall()
    json_result = [dict(r) for r in query_result]
    return json_result


tool_schemas = [query_datasource.openai_schema]
