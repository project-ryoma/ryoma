from typing import Dict, Optional

from aita.agent.graph import WorkflowAgent
from aita.tool.sql_tool import (
    ConvertToArrowTool,
    ConvertToPandasTool,
    CreateTableTool,
    SqlQueryTool,
)


class SqlAgent(WorkflowAgent):
    description: str = "A SQL agent that can use SQL Tools to interact with SQL databases."

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
    ):
        super().__init__(
            [SqlQueryTool(), CreateTableTool(), ConvertToArrowTool()],
            model,
            model_parameters,
        )
