from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy.engine import Result
from typing import Any, Union, Sequence, Dict, Type
import logging
from aita.datasource.base import SqlDataSource
from IPython import get_ipython
from IPython.core.interactiveshell import InteractiveShell, ExecutionResult

log = logging.getLogger(__name__)


class QueryInput(BaseModel):
    query: str = Field(description="sql data query")


class QuerySQLDataBaseTool(BaseTool):
    """Tool for querying a SQL database."""
    datasource: SqlDataSource = Field(exclude=True)
    name: str = "sql_datasource_query"
    description: str = """
    Execute a SQL query against the database and get back the result..
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    args_schema: Type[BaseModel] = QueryInput

    class Config(BaseTool.Config):
        pass

    def _run(
        self,
        query,
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        return self.datasource.execute(query)


class ConvertToPandasTool(BaseTool):
    """Tool for converting a SQL query result to a pandas dataframe."""

    name: str = "convert_to_pandas"
    description: str = """
    Convert a SQL query result to a pandas dataframe.
    If the query result is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = QueryInput

    def _run(
        self,
        query,
        **kwargs,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        return self.datasource.to_pandas(query)


# class ExtractMetadataTool(BaseTool):
#     """Tool form extracting metadata from a data source."""
#
#     datasource: SqlDataSource = Field(exclude=True)
#     name: str = "extract_metadata"
#     description: str = """
#     Extract metadata from a data source.
#     If the data source is not correct, an error message will be returned.
#     """
#     args_schema: Type[BaseModel] = QueryInput
#
#     def _run(
#         self,
#         query,
#         **kwargs,
#     ) -> Union[str, Sequence[Dict[str, Any]], Result]:
#         """Execute the query, return the results or an error message."""
#         return self.datasource.get_metadata()


class PythonInput(BaseModel):
    script: str = Field(description="python script")


class IPythonTool(BaseTool):
    """Tool for running python script in an IPython environment."""

    name: str = "run_ipython_script_tool"
    description: str = """
    Execute a python script in an IPython environment and return the result of the last expression.
    If the script is not correct, an error message will be returned.
    """
    args_schema: Type[BaseModel] = PythonInput

    script_context: Dict[str, Any] = Field(
        description="context for the script execution"
    )

    def _run(
        self,
        script,
    ) -> Union[str, Sequence[Dict[str, Any]], ExecutionResult]:
        """Execute the script, return the result or an error message."""
        try:
            ipython = get_ipython()
            if not ipython:
                ipython = InteractiveShell()

            ipython.user_ns.update(self.script_context)

            result = ipython.run_cell(script)
            return result
        except Exception as e:
            return str(e)


class PandasTool(IPythonTool):
    """Tool for running Pandas analysis."""

    name: str = "pandas_analysis_tool"
    description: str = """
    Run a pandas analysis script.
    The last line of the script should return a pandas dataframe.
    If the script is not correct, an error message will be returned.
    """


class PySparkTool(IPythonTool):
    """Tool for running PySpark script."""

    name: str = "pyspark_tool"
    description: str = """
    Run a PySpark analysis script.
    The last line of the script should return a PySpark dataframe.
    If the script is not correct, an error message will be returned.
    """
