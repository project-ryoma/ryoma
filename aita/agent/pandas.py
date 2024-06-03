from typing import Dict

from pandas import DataFrame

from aita.agent.base import ToolAgent
from aita.tool.pandas import PandasTool
from aita.tool.python import PythonTool
from aita.tool.sql import ConvertToPandasTool


class PandasAgent(ToolAgent):

    def __init__(self, model: str, model_parameters: Dict = None):
        super().__init__(
            [
                PandasTool(),
                ConvertToPandasTool(),
            ],
            model,
            model_parameters,
        )

    def add_dataframe(self, dataframe: DataFrame):
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
