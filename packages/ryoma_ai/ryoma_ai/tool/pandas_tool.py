from typing import Optional, Type

from pydantic import BaseModel, Field
from ryoma_ai.tool.python_tool import PythonTool
from ryoma_data.base import DataSource


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
    datasource: Optional[DataSource] = Field(
        None, exclude=True, description="Data source"
    )

    args_schema: Type[BaseModel] = PandasInput
