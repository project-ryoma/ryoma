from enum import Enum

from aita.tool.sql import SqlQueryTool
from aita.tool.python import PythonTool
from aita.tool.pandas import PandasTool
from aita.tool.pyarrow import ArrowTool
from aita.tool.pyspark import PySparkTool


class ToolProvider(Enum):
    sql = SqlQueryTool
    python = PythonTool
    pandas = PandasTool
    pyarrow = ArrowTool
    pyspark = PySparkTool


def get_supported_tools():
    return list(ToolProvider)


class ToolFactory:
    @staticmethod
    def create_tool(tool: str, *args, **kwargs):
        if not hasattr(ToolProvider, tool):
            raise ValueError(f"Unsupported tool: {tool}")

        tool_class = ToolProvider[tool].value
        return tool_class(*args, **kwargs)
