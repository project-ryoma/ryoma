from typing import Dict
from aita.agent.base import ToolAgent
from aita.tool.pyarrow_tool import ArrowTool, ConvertToArrowTool
from aita.datasource.base import DataSource
from pyarrow import Table


class PyArrowAgent(ToolAgent):
    prompt_context = """
    Meta data of all available data sources:
    {script_context}

    pyarrow table can be created by using the data source as:
    datasource.to_arrow(query)
    """

    def __init__(self, datasource: [DataSource, Table], model_id: str, model_parameters: Dict = None):
        self.prompt_context = self.prompt_context.format(script_context=datasource.get_metadata())
        super().__init__([
            ConvertToArrowTool(datasource=datasource),
            ArrowTool(script_context={"table": datasource})
        ], model_id, model_parameters, prompt_context=self.prompt_context)
