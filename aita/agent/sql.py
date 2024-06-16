from typing import Dict, Optional

from aita.agent.graph import GraphAgent
from aita.tool.sql import ConvertToArrowTool, ConvertToPandasTool, CreateTableTool, SqlQueryTool


class SqlAgent(GraphAgent):

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
    ):
        super().__init__(
            [SqlQueryTool(), CreateTableTool(), ConvertToArrowTool(), ConvertToPandasTool()],
            model,
            model_parameters,
        )
