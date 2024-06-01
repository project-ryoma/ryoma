from typing import Type

from langchain_core.pydantic_v1 import BaseModel, Field

from aita.tool.python import PythonTool


class PandasInput(BaseModel):
    script: str = Field(description="pandas script")


class PandasTool(PythonTool):
    """Tool for running Pandas analysis."""

    name: str = "pandas_analysis_tool"
    description: str = """
    Run a pandas analysis script.
    If the script is not correct, an error message will be returned.

    Pandas dataframe is available in the script context.
    """

    args_schema: Type[BaseModel] = PandasInput
