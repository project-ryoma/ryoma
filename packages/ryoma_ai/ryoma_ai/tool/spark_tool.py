import pandas as pd
from ryoma_ai.tool.python_tool import PythonTool


class SparkTool(PythonTool):
    """Tool for running PySpark script."""

    name: str = "pyspark_tool"
    description: str = """
    Run a PySpark analysis script.
    The last line of the script should return a PySpark dataframe.
    If the script is not correct, an error message will be returned.
    """


class ConvertPandasToSparkTool(PythonTool):
    """Tool for converting a Pandas dataframe to a PySpark dataframe."""

    name: str = "convert_pandas_to_pyspark"
    description: str = """
    Convert a Pandas dataframe to a PySpark dataframe.
    If the Pandas dataframe is not correct, an error message will be returned.
    """

    def _run(self, dataframe: pd.DataFrame, **kwargs):
        """Convert the Pandas dataframe to a PySpark dataframe."""
        return self.script_context["spark_session"].createDataFrame(dataframe)
