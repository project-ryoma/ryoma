from typing import Dict

import pandas as pd

from aita.agent.base import AitaAgent
from aita.tool.pandas import PandasTool


class PandasAgent(AitaAgent):

    prompt_context = """
    Meta data of all available data source as pandas dataframe:
    {script_context}
    """

    def __init__(
        self, dataframes: Dict[str, pd.DataFrame], model_id: str, model_parameters: Dict = None
    ):
        tool = PandasTool(script_context=dataframes)
        dataframe_metadata = []
        for name, df in dataframes.items():
            dataframe_metadata.append({"name": name, "columns": df.columns.tolist()})
        self.prompt_context = self.prompt_context.format(script_context=dataframe_metadata)
        super().__init__(model_id, model_parameters, [tool], prompt_context=self.prompt_context)
