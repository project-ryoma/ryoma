from abc import ABC
from typing import Any, Dict, Sequence, Type, Union, Optional

import pandas as pd
from IPython import get_ipython
from IPython.core.interactiveshell import ExecutionResult, InteractiveShell
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from aita.tool.base import DataSourceTool
from aita.tool.ipython import PythonTool


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


class ConvertInput(BaseModel):
    query: str = Field(description="sql data query")


class ConvertToPandasTool(DataSourceTool):
    """Tool for converting a SQL query result to a pandas dataframe."""

    name: str = "convert_to_pandas"
    description: str = """
    Convert a SQL query result to a pandas dataframe.
    If the query result is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = ConvertInput

    def _run(
        self,
        query: str,
        **kwargs,
    ) -> pd.DataFrame:
        """Execute the query, return the results or an error message."""
        return self.datasource.to_pandas(query)
