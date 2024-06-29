from typing import Dict

from pandas import DataFrame

from aita.agent.graph import GraphAgent
from aita.tool.pandas_tool import PandasTool
from aita.tool.python_tool import PythonTool
from aita.tool.sql_tool import ConvertToPandasTool


class PandasAgent(GraphAgent):
    type: str = "pandas"
    description: str = (
        "A pandas agent that can use pandas tools to interact with pandas DataFrames."
    )

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
        self.add_prompt_context(
            f"""
        dataframe name: {df_id}
        dataframe metadata: {dataframe.info}
        """
        )
        for tool in self.tools:
            if isinstance(tool, PythonTool):
                tool.update_script_context(script_context={df_id: dataframe})
        return self
