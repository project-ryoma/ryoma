from typing import Type

from langchain_core.pydantic_v1 import BaseModel, Field
from ryoma_ai.tool.python_tool import PythonTool


class ArrowInput(BaseModel):
    script: str = Field(description="PyArrow analysis script")


class ArrowTool(PythonTool):
    """Tool for using Apache Arrow in Python."""

    name: str = "pyarrow_tool"
    description: str = """
    Apache Arrow is a cross-language development platform for in-memory data analysis.
    This tool allows you to run PyArrow script in Python.

    PyArrow Table is available in the script context.
    """
    args_schema: Type[BaseModel] = ArrowInput
