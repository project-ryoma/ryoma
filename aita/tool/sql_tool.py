from typing import Any, Dict, Sequence, Type, Union

from pydantic import BaseModel, Field
from sqlalchemy.engine import Result

from aita.datasource.sql import SqlDataSource
from aita.tool.ipython import BaseTool
from aita.datasource.catalog import Table


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


class CreateTableTool(BaseTool):
    """Tool for creating a table in a SQL database."""

    datasource: SqlDataSource = Field(exclude=True)
    name: str = "create_table"
    description: str = """
    Create a table in the database.
    If the table already exists, an error message will be returned.
    input arguments are table_name and table_columns.
    """
    args_schema: Type[BaseModel] = Table

    def _run(
        self,
        table_name,
        table_columns,
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        columns = ",\n".join(
            f"{column.column_name} \"{column.xdbc_type_name}\""
            for column in table_columns
        )
        return self.datasource.execute(
            "CREATE TABLE {table_name} ({columns})".format(table_name=table_name, columns=columns))


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
