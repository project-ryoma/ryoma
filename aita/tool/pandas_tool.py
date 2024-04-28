from aita.tool.ipython import IPythonTool


class PandasTool(IPythonTool):
    """Tool for running Pandas analysis."""

    name: str = "pandas_analysis_tool"
    description: str = """
    Run a pandas analysis script.
    The last line of the script should return a pandas dataframe.
    If the script is not correct, an error message will be returned.
    """
