from typing import Dict

from aita.agent.base import ToolAgent
from aita.tool.pandas_tool import PandasTool
from aita.datasource.base import DataSource


class PandasAgent(ToolAgent):
    prompt_context = """
    Meta data of all available data sources
    {script_context}

    Pandas dataframe can be created by using the data source as:
    datasource.to_pandas(query)
    """

    def __init__(
        self, datasource: DataSource, model: str, model_parameters: Dict = None
    ):
        tool = PandasTool(script_context={"dataframe": datasource})
        self.prompt_context = self.prompt_context.format(script_context=datasource.get_metadata())
        super().__init__(model, [tool], model_parameters, prompt_context=self.prompt_context)
