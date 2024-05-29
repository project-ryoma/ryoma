from typing import Union

from langchain_core.pydantic_v1 import Field

from aita.datasource.base import DataSource
from aita.tool.ipython import PythonTool
from pyarrow import Table


class ArrowTool(PythonTool):
    """Tool for using Apache Arrow in Python."""

    name: str = "pyarrow_tool"
    description: str = """
    Apache Arrow is a cross-language development platform for in-memory data analysis.
    This tool allows you to run Apache Arrow scripts in Python.

    PyArrow Table can be accessed using the variable 'table'.
    """


class ConvertToArrowTool(PythonTool):
    """Tool for converting a pandas dataframe to an Apache Arrow table."""

    datasource: DataSource = Field(exclude=True)
    name: str = "convert_to_arrow"
    description: str = """
    Convert a pandas dataframe to an Apache Arrow table.
    If the dataframe is not correct, an error message will be returned.
    """

    def _run(
        self,
        dataframe,
        **kwargs,
    ) -> Union[str, Table]:
        """Convert the dataframe to an Apache Arrow table."""
        return self.datasource.to_arrow(dataframe)
