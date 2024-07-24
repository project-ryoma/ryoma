from typing import Any, Dict, Literal, Optional, Sequence, Type, Union

import base64
import pickle
from abc import ABC

import pandas as pd
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from sqlalchemy.engine import Result

from aita.datasource.ds_ibis import IbisDataSource
from aita.datasource.sql import SqlDataSource


class SqlDataSourceTool(BaseTool, ABC):
    datasource: Optional[IbisDataSource] = Field(None, exclude=True)

    class Config(BaseTool.Config):
        pass


class QueryInput(BaseModel):
    query: str = Field(description="sql query that can be executed by the sql database.")
    result_format: Optional[Literal["pandas", "arrow", "polars"]] = Field(
        description="Format of the result, currently supports pandas, arrow, and polars. Default is pandas."
    )


class SqlQueryTool(SqlDataSourceTool):
    """Tool for querying a SQL database."""

    name: str = "sql_database_query"
    description: str = """
    Execute a SQL query against the database and get back the result..
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    args_schema: Type[BaseModel] = QueryInput
    response_format: Literal["content", "content_and_artifact"] = "content_and_artifact"

    def _run(
        self,
        query,
        result_format: Optional[Literal["pandas", "arrow", "polars"]] = "pandas",
        **kwargs,
    ) -> (str, str):
        """Execute the query, return the results or an error message."""
        try:
            result = self.datasource.execute(query, result_format=result_format)

            # Serialize the result to a base64 encoded string as the artifact
            artifact = base64.b64encode(pickle.dumps(result)).decode("utf-8")
            return result, artifact
        except Exception as e:
            return "Received an error while executing the query: {}".format(str(e)), ""


class Column(BaseModel):
    column_name: str = Field(..., description="Name of the column")
    column_type: str = Field(..., description="Type of the column")
    nullable: Optional[bool] = Field(None, description="Whether the column is nullable")
    primary_key: Optional[bool] = Field(None, description="Whether the column is a primary key")


class Table(BaseModel):
    table_name: str = Field(..., description="Name of the table")
    table_columns: Sequence[Column] = Field(..., description="List of columns in the table")
    table_type: Optional[str] = Field(..., description="Type of the table")


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
        table_name: str,
        table_columns: Sequence[Column],
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        columns = ",\n".join(
            f'{column.column_name} "{column.column_type}"' for column in table_columns
        )
        return self.datasource.execute(
            "CREATE TABLE {table_name} ({columns})".format(table_name=table_name, columns=columns)
        )


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
