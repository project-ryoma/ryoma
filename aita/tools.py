from langchain_community.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.tools import BaseTool
from sqlalchemy.engine import Result
from typing import Any, Union, Sequence, Dict
import logging

log = logging.getLogger(__name__)


class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name: str = "sql_db_query"
    description: str = """
    Execute a SQL query against the database and get back the result..
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """

    def _run(
        self,
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        if "__arg1" in kwargs:
            query = kwargs.get("__arg1")
            return self.db.run_no_throw(query)
        else:
            raise ValueError("Missing query input.")
