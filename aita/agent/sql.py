from typing import Dict, Optional

from aita.agent.base import ToolAgent
from aita.datasource.sql import SqlDataSource
from aita.tool.sql_tool import SqlDatabaseTool, CreateTableTool


class SqlAgent(ToolAgent):

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
    ):
        super().__init__([
            SqlDatabaseTool(),
            CreateTableTool(),
        ], model, model_parameters)
