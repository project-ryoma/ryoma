from typing import Dict
from aita.agent.base import AitaAgent
from aita.tool.pyarrow_tool import ArrowTool
from aita.datasource.base import DataSource


class PyArrowAgent(AitaAgent):

    prompt_context = """
    Meta data of all available data sources:
    {script_context}

    pyarrow table can be created by using the data source as:
    datasource.to_arrow(query)
    """

    def __init__(self, datasource: DataSource, model_id: str, model_parameters: Dict = None):
        tool = ArrowTool(script_context={"datasource": datasource})
        self.prompt_context = self.prompt_context.format(script_context=datasource.get_metadata())
        super().__init__(model_id, model_parameters, [tool], prompt_context=self.prompt_context)
