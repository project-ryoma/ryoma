from typing import List, Dict
from pyspark.sql import DataFrame
from aita.agent.base import AitaAgent
from aita.tool.spark import PySparkTool


class PySparkAgent(AitaAgent):
    dataframes: List[DataFrame]

    prompt_context = """
    Meta data of all available data source as pyspark dataframe:
    {dataframe_metadata}
    """

    def __init__(self, dataframes: Dict[str, DataFrame], model, temperature):
        tool = PySparkTool(script_context=dataframes)
        dataframe_metadata = []
        for name, df in dataframes.items():
            dataframe_metadata.append({
                "name": name,
                "columns": df.columns
            })
        self.prompt_context = self.prompt_context.format(dataframe_metadata=dataframe_metadata)
        super().__init__(model, temperature, [tool], prompt_context=self.prompt_context)
