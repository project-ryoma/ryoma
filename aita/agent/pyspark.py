from typing import Dict, Union

import findspark
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame

from aita.agent.base import ToolAgent
from aita.tool.pyspark_tool import PySparkTool, ConvertPandasToPySparkTool
from aita.tool.pandas_tool import ConvertToPandasTool
from aita.datasource.base import DataSource


class PySparkAgent(ToolAgent):
    prompt_context = """
    Meta data of all available data sources as PySpark DataFrame:
    {dataframe_metadata}
    """

    spark_session: SparkSession

    def __init__(self,
                 datasource: Union[DataSource, pd.DataFrame, DataFrame],
                 spark_configs: dict[str, str],
                 model: str,
                 model_parameters=None):
        assert "master" in spark_configs, "master is required in spark_configs"
        assert "app_name" in spark_configs, "app_name is required in spark_configs"
        self.init_session(spark_configs)

        self.prompt_context = self.prompt_context.format(dataframe_metadata=datasource.get_metadata())
        tools = self.create_spark_tools(datasource)
        super().__init__(tools, model, model_parameters, prompt_context=self.prompt_context)

    def init_session(self, spark_configs: dict[str, str]):
        self.spark_session = self.create_spark_session(spark_configs)
        self.spark_session.conf.set("spark.sql.execution.arrow.enabled", "true")

    def create_spark_tools(self, datasource: Union[DataSource, pd.DataFrame, DataFrame]):
        script_context = {"spark_session": self.spark_session, **datasource}
        return [
            PySparkTool(script_context=script_context),
            ConvertPandasToPySparkTool(script_context=script_context),
            ConvertToPandasTool(datasource=datasource)
        ]

    @staticmethod
    def create_spark_session(configs):
        master = configs.get("master", "local")
        app_name = configs.get("app_name", "aita")
        findspark.init()
        return SparkSession.builder.master(master).appName(app_name).getOrCreate()
