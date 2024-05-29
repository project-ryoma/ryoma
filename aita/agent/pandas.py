from typing import Dict, Union

from aita.agent.base import ToolAgent
from aita.tool.pandas_tool import PandasTool, ConvertToPandasTool
from pandas import DataFrame

from aita.tool.ipython import PythonTool


class PandasAgent(ToolAgent):

    def __init__(
        self, model: str, model_parameters: Dict = None
    ):
        super().__init__([
            ConvertToPandasTool(),
            PandasTool()
        ], model, model_parameters)

    def add_dataframe(self, dataframe: DataFrame):
        self.set_prompt_template(dataframe.info())
        for tool in self.tools:
            if isinstance(tool, PythonTool):
                tool.update_script_context(script_context=dataframe)
        return self
