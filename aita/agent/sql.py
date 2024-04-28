from typing import Dict, Optional

from aita.agent.base import AitaAgent
from aita.datasource.base import SqlDataSource
from aita.tool.sql import SqlDatabaseTool


class SqlAgent(AitaAgent):

    prompt_context = """
    database metadata: {metadata}
    """

    def __init__(
        self,
        datasource: SqlDataSource,
        model_id: str,
        model_parameters: Optional[Dict] = None,
        allow_extract_metadata=False,
    ):
        tools = [
            SqlDatabaseTool(datasource=datasource),
        ]
        if allow_extract_metadata:
            metadata = datasource.get_metadata()
            self.prompt_context = self.prompt_context.format(metadata=metadata)
        super().__init__(model_id, model_parameters, tools, prompt_context=self.prompt_context)
