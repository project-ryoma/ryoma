from typing import Type

from langchain_core.pydantic_v1 import BaseModel, Field

from aita.tool.python import PythonTool


class PandasInput(BaseModel):
    script: str = Field(description="pandas script")


class PandasTool(PythonTool):
    """Tool for running Pandas analysis."""

    name: str = "pandas_tool"
    description: str = """
    Run a python script by using the Pandas library.
    If the script is not correct, an error message will be returned.

    Pandas dataframes are stored in the script context.
    """

    args_schema: Type[BaseModel] = PandasInput
