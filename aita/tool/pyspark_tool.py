from aita.tool.ipython import PythonTool


class PySparkTool(PythonTool):
    """Tool for running PySpark script."""

    name: str = "pyspark_tool"
    description: str = """
    Run a PySpark analysis script.
    The last line of the script should return a PySpark dataframe.
    If the script is not correct, an error message will be returned.
    """
