from typing import Any, Dict, Optional, Sequence, Type, Union

from abc import ABC

import pandas as pd
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from sqlalchemy.engine import Result

from aita.datasource.catalog import Table
from aita.datasource.sql import SqlDataSource


class SqlDataSourceTool(BaseTool, ABC):
    datasource: Optional[SqlDataSource] = Field(None, exclude=True)

    class Config(BaseTool.Config):
        pass


class QueryInput(BaseModel):
    query: str = Field(description="sql query that can be executed by the sql database.")


class SqlQueryTool(SqlDataSourceTool):
    """Tool for querying a SQL database."""

    name: str = "sql_database_query"
    description: str = """
    Execute a SQL query against the database and get back the result..
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    args_schema: Type[BaseModel] = QueryInput

    def _run(
        self,
        query,
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        return self.datasource.execute(query)


class CreateTableTool(SqlDataSourceTool):
    """Tool for creating a table in a SQL database."""

    datasource: Optional[SqlDataSource] = Field(None, exclude=True)
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


class ConvertToPandasTool(SqlDataSourceTool):
    """Tool for converting a SQL query result to a pandas dataframe."""

    name: str = "convert_to_pandas"
    description: str = """
    Convert a SQL query result to a pandas dataframe.
    The tool can only be used if the data source is provided.
    If the query result is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = QueryInput

    def _run(
        self,
        query: str,
        **kwargs,
    ) -> pd.DataFrame:
        """Execute the query, return the result as pandas or an error message."""
        return self.datasource.to_pandas(query)


class ConvertToArrowTool(SqlDataSourceTool):
    """Tool for converting a SQL query result to a PyArrow Table."""

    name: str = "convert_to_arrow"
    description: str = """
    Convert a SQL query result to a PyArrow Table.
    If the query result is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = QueryInput

    def _run(
        self,
        query: str,
        **kwargs,
    ) -> Table:
        """Execute the query, return the results or an error message."""
        return self.datasource.to_arrow(query)
