from typing import Any, Dict, Sequence, Type, Union

from pydantic import BaseModel, Field
from sqlalchemy.engine import Result

from aita.datasource.base import SqlDataSource
from aita.tool.ipython import BaseTool


class QueryInput(BaseModel):
    query: str = Field(description="sql data query")


class SqlDatabaseTool(BaseTool):
    """Tool for querying a SQL database."""

    datasource: SqlDataSource = Field(exclude=True)
    name: str = "sql_database_query"
    description: str = """
    Execute a SQL query against the database and get back the result..
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    args_schema: Type[BaseModel] = QueryInput

    class Config(BaseTool.Config):
        pass

    def _run(
        self,
        query,
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        return self.datasource.execute(query)


class ConvertToPandasTool(BaseTool):
    """Tool for converting a SQL query result to a pandas dataframe."""

    name: str = "convert_to_pandas"
    description: str = """
    Convert a SQL query result to a pandas dataframe.
    If the query result is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = QueryInput

    def _run(
        self,
        query,
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        return self.datasource.to_pandas(query)
