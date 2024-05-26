from typing import Dict, Optional

from aita.agent.base import AitaAgent
from aita.datasource.sql import SqlDataSource
from aita.tool.sql_tool import SqlDatabaseTool, CreateTableTool


class SqlAgent(AitaAgent):

    prompt_context = """
    You are provided with sql data sources:
    {metadata}
    """

    def __init__(
        self,
        datasource: SqlDataSource,
        model_id: str,
        model_parameters: Optional[Dict] = None,
        allow_extract_metadata=False,
        prompt_context=None,
    ):
        tools = [
            SqlDatabaseTool(datasource=datasource),
            CreateTableTool(datasource=datasource),
        ]
        if prompt_context:
            self.prompt_context = prompt_context
        elif allow_extract_metadata:
            self.prompt_context = self.generate_prompt_context(datasource)
        super().__init__(model_id, model_parameters, tools, prompt_context=self.prompt_context)

    def generate_prompt_context(self, datasource: SqlDataSource):
        metadata = datasource.get_metadata().json()
        return self.prompt_context.format(metadata=metadata)
