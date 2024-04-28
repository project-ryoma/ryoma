from typing import Dict

import findspark
import pandas as pd
from pyspark.sql import SparkSession

from aita.agent.base import AitaAgent
from aita.tool.pyspark_tool import PySparkTool


class PySparkAgent(AitaAgent):

    prompt_context = """
    Meta data of all available data sources as Pandas DataFrame:
    {dataframe_metadata}
    """

    spark_session: SparkSession

    def __init__(self, dataframes: Dict[str, pd.DataFrame], model, temperature):
        self.spark_session = self.create_spark_session()
        tool = self.create_spark_tool(dataframes)
        dataframe_metadata = []
        for name, df in dataframes.items():
            dataframe_metadata.append({"name": name, "schema": df.info})
        self.prompt_context = self.prompt_context.format(dataframe_metadata=dataframe_metadata)
        super().__init__(model, temperature, [tool], prompt_context=self.prompt_context)

    def create_spark_tool(self, dataframes: Dict[str, pd.DataFrame]):
        script_context = {"spark_session": self.spark_session, **dataframes}
        return PySparkTool(script_context=script_context)

    @staticmethod
    def create_spark_session():
        findspark.init()
        return SparkSession.builder.master("local").appName("aita").getOrCreate()
