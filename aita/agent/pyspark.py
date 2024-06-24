import findspark
import pandas as pd
from pyspark.sql import SparkSession

from aita.agent.graph import GraphAgent
from aita.tool.pyspark_tool import ConvertPandasToPySparkTool, PySparkTool
from aita.tool.python_tool import PythonTool


class PySparkAgent(GraphAgent):
    type: str = "pyspark"
    spark_session: SparkSession

    def __init__(self, spark_configs: dict[str, str], model: str, model_parameters=None):
        self.init_session(spark_configs)
        super().__init__(
            [
                PySparkTool(),
                ConvertPandasToPySparkTool(),
            ],
            model,
            model_parameters,
        )
        for tool in self.tools:
            if isinstance(tool, PythonTool):
                tool.update_script_context(script_context={"spark_session": self.spark_session})

    def init_session(self, spark_configs: dict[str, str]):
        self.spark_session = self.create_spark_session(spark_configs)
        self.spark_session.conf.set("spark.sql.execution.arrow.enabled", "true")

    @staticmethod
    def create_spark_session(spark_configs: dict[str, str]):
        assert "master" in spark_configs, "master is required in spark_configs"
        assert "app_name" in spark_configs, "app_name is required in spark_configs"
        findspark.init()
        return (
            SparkSession.builder.master(spark_configs.get("master"))
            .appName(spark_configs.get("app_name"))
            .getOrCreate()
        )

    def add_pandas_dataframe(self, dataframe: pd.DataFrame):
        df_id = f"df_{id(dataframe)}"
        self._fill_prompt_context(
            f"""
        dataframe name: {df_id}
        dataframe metadata: {dataframe.info}
        """
        )
        for tool in self.tools:
            if isinstance(tool, PythonTool):
                tool.update_script_context(script_context={df_id: dataframe})
        return self
