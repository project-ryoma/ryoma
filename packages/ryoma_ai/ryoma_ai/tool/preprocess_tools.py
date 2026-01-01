from typing import Type

from langchain_core.tools import BaseTool, InjectedToolArg
from pydantic import BaseModel, Field
from ryoma_data.base import DataSource
from ryoma_data.sql import SqlDataSource
from ryoma_ai.utils import ensure_sql_datasource
from typing_extensions import Annotated


# Tool 1: Summarize Table
class SummarizeTableInput(BaseModel):
    table_name: str = Field(..., description="Name of the table to summarize.")
    datasource: Annotated[DataSource, InjectedToolArg] = Field(
        description="Data source containing the table."
    )

    model_config = {"arbitrary_types_allowed": True}


class SummarizeTableTool(BaseTool):
    name = "summarize_table"
    description = "Summarize schema and column semantics of a given SQL table."
    args_schema: Type[BaseModel] = SummarizeTableInput

    def __init__(self, summarizer, **kwargs):
        super().__init__(**kwargs)
        self.summarizer = summarizer

    def _run(self, table_name: str, datasource: DataSource, **kwargs) -> str:
        # Ensure we have a SQL datasource
        sql_datasource = ensure_sql_datasource(datasource)
        profile = sql_datasource.profile_table(table_name)
        return self.summarizer.summarize_schema(profile)


# Tool 2: Schema Linking / SQL Generation
class GenerateSQLInput(BaseModel):
    user_question: str = Field(
        ..., description="Natural language user question to convert into SQL."
    )
    table_name: str = Field(..., description="Name of the table to query.")
    datasource: Annotated[DataSource, InjectedToolArg] = Field(
        description="Data source for schema linking."
    )

    model_config = {"arbitrary_types_allowed": True}


class SchemaLinkingTool(BaseTool):
    name = "generate_sql_with_schema_reasoning"
    description = "Generate SQL using schema-level understanding of a given table."
    args_schema: Type[BaseModel] = GenerateSQLInput

    def __init__(self, schema_linker, **kwargs):
        super().__init__(**kwargs)
        self.schema_linker = schema_linker

    def _run(self, user_question: str, table_name: str, **kwargs) -> str:
        return self.schema_linker.refine_sql(user_question, table_name)


# Tool 3: SQL → Natural Language
class SQLInterpretationInput(BaseModel):
    sql_query: str = Field(..., description="SQL query to interpret.")
    table_name: str = Field(
        ..., description="Name of the table referenced by the query."
    )
    datasource: Annotated[DataSource, InjectedToolArg] = Field(
        description="Data source used for column metadata."
    )

    model_config = {"arbitrary_types_allowed": True}


class SQLInterpretationTool(BaseTool):
    name = "interpret_sql"
    description = (
        "Interpret a SQL query and convert it to a natural language explanation."
    )
    args_schema: Type[BaseModel] = SQLInterpretationInput

    def __init__(self, log_converter, **kwargs):
        super().__init__(**kwargs)
        self.log_converter = log_converter

    def _run(self, sql_query: str, table_name: str, **kwargs) -> str:
        return self.log_converter.generate_nl_from_sql(sql_query, table_name)
