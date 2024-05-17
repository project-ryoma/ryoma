from typing import Dict


from aita.agent.base import AitaAgent
from aita.tool.pandas_tool import PandasTool
from aita.datasource.base import DataSource


class PandasAgent(AitaAgent):

    prompt_context = """
    Meta data of all available data sources
    {script_context}

    Pandas dataframe can be created by using the data source as:
    datasource.to_pandas(query)
    """

    def __init__(
        self, datasource: DataSource, model_id: str, model_parameters: Dict = None
    ):

        tool = PandasTool(script_context={"datasource": datasource})
        self.prompt_context = self.prompt_context.format(script_context=datasource.get_metadata())
        super().__init__(model_id, model_parameters, [tool], prompt_context=self.prompt_context)


