from enum import Enum

from aita.tool.pandas_tool import PandasTool
from aita.tool.pyarrow_tool import ArrowTool
from aita.tool.pyspark_tool import PySparkTool
from aita.tool.python_tool import PythonTool
from aita.tool.sql_tool import SqlQueryTool


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
