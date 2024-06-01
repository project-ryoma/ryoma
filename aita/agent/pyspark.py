import findspark
from pyspark.sql import SparkSession

from aita.agent.base import ToolAgent
from aita.tool.pyspark import PySparkTool, ConvertPandasToPySparkTool
from aita.tool.python import PythonTool


class PySparkAgent(ToolAgent):
    spark_session: SparkSession

    def __init__(self,
                 spark_configs: dict[str, str],
                 model: str,
                 model_parameters=None):
        self.init_session(spark_configs)

        super().__init__([
            PySparkTool(script_context=self.spark_session),
            ConvertPandasToPySparkTool(script_context=self.spark_session),
        ], model, model_parameters)

    def init_session(self, spark_configs: dict[str, str]):
        self.spark_session = self.create_spark_session(spark_configs)
        self.spark_session.conf.set("spark.sql.execution.arrow.enabled", "true")

    @staticmethod
    def create_spark_session(spark_configs: dict[str, str]):
        assert "master" in spark_configs, "master is required in spark_configs"
        assert "app_name" in spark_configs, "app_name is required in spark_configs"
        findspark.init()
        return SparkSession.builder.master(spark_configs.get("master")).appName(
            spark_configs.get("app_name")).getOrCreate()

    def add_dataframe(self, dataframe):
        self._set_prompt_context(dataframe.info)
        for tool in self.tools:
            if isinstance(tool, PythonTool):
                tool.update_script_context(script_context=self.spark_session)
        return self
