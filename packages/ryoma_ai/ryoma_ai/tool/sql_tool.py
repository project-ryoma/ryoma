import base64
import pickle
from abc import ABC
from typing import Any, Dict, Literal, Optional, Sequence, Type, Union

from langchain_core.tools import BaseTool, InjectedToolArg
from pydantic import BaseModel, Field
from ryoma_ai.datasource.sql import SqlDataSource
from sqlalchemy.engine import Result
from typing_extensions import Annotated


class QueryInput(BaseModel):
    query: str = Field(description="sql query that can be executed by the sql catalog.")
    datasource: Annotated[SqlDataSource, InjectedToolArg] = Field(
        description="sql data source that can be used to execute the query."
    )

    model_config = {"arbitrary_types_allowed": True}


class SqlQueryTool(BaseTool):
    """Tool for querying a SQL catalog."""

    name: str = "sql_database_query"
    description: str = """
    Execute a SQL query against the catalog and get back the result..
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    args_schema: Type[BaseModel] = QueryInput
    response_format: Literal["content", "content_and_artifact"] = "content_and_artifact"

    def _run(
        self,
        query,
        datasource: SqlDataSource,
        **kwargs,
    ) -> (str, str):
        """Execute the query, return the results or an error message."""
        try:
            result = datasource.query(query)

            # Serialize the result to a base64 encoded string as the artifact
            artifact = base64.b64encode(pickle.dumps(result)).decode("utf-8")
            return result, artifact
        except Exception as e:
            return f"Received an error while executing the query: {str(e)}", ""


class Column(BaseModel):
    column_name: str = Field(..., description="Name of the column")
    column_type: str = Field(..., description="Type of the column")
    nullable: Optional[bool] = Field(None, description="Whether the column is nullable")
    primary_key: Optional[bool] = Field(
        None, description="Whether the column is a primary key"
    )


class CreateTableInputSchema(BaseModel):
    datasource: Annotated[SqlDataSource, InjectedToolArg] = Field(
        description="sql data source that can be used to execute the query."
    )
    table_name: str = Field(..., description="Name of the table")
    table_columns: Sequence[Column] = Field(
        ..., description="List of columns in the table"
    )
    table_type: Optional[str] = Field(..., description="Type of the table")


class CreateTableTool(BaseTool):
    """Tool for creating a table in a SQL catalog."""

    name: str = "create_table"
    description: str = """
    Create a table in the catalog.
    If the table already exists, an error message will be returned.
    input arguments are table_name and table_columns.
    """
    args_schema: Type[BaseModel] = CreateTableInputSchema

    def _run(
        self,
        datasource: SqlDataSource,
        table_name: str,
        table_columns: Sequence[Column],
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        columns = ",\n".join(
            f'{column.column_name} "{column.column_type}"' for column in table_columns
        )
        return datasource.query(
            "CREATE TABLE {table_name} ({columns})".format(
                table_name=table_name, columns=columns
            )
        )


class QueryPlanTool(BaseTool):
    """Tool for getting the query plan of a SQL query."""

    name: str = "query_plan"
    description: str = """
    Get the query plan of a SQL query.
    If the query is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = QueryInput

    def _run(
        self,
        query: str,
        datasource: SqlDataSource,
        **kwargs,
    ) -> str:
        """Execute the query, return the results or an error message."""
        return self.datasource.get_query_plan(query)


class QueryProfileTool(BaseTool):
    """Tool for getting the query profile of a SQL query."""

    name: str = "query_profile"
    description: str = """
    Get the query profile of a SQL query.
    If the query is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = QueryInput

    def _run(
        self,
        query: str,
        datasource: SqlDataSource,
        **kwargs,
    ) -> str:
        """Execute the query, return the results or an error message."""
        return self.datasource.get_query_profile(query)
