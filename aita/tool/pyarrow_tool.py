from aita.tool.ipython import IPythonTool


class ArrowTool(IPythonTool):
    """Tool for using Apache Arrow in Python."""

    name: str = "pyarrow_tool"
    description: str = """
    Apache Arrow is a cross-language development platform for in-memory data analysis.
    This tool allows you to run Apache Arrow scripts in Python.
    """
