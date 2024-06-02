from typing import Dict, Optional

from aita.agent.base import ToolAgent
from aita.tool.sql import ConvertToArrowTool, ConvertToPandasTool, CreateTableTool, SqlQueryTool


class SqlAgent(ToolAgent):

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
    ):
        super().__init__([
            SqlQueryTool(),
            CreateTableTool(),
            ConvertToArrowTool(),
            ConvertToPandasTool()
        ], model, model_parameters)
