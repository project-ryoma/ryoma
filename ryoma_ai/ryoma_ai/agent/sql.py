from typing import Dict, Optional

from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.tool.sql_tool import CreateTableTool, QueryProfileTool, SqlQueryTool


class SqlAgent(WorkflowAgent):
    description: str = (
        "A SQL agent that can use SQL Tools to interact with SQL schemas."
    )

    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
    ):
        super().__init__(
            [SqlQueryTool(), CreateTableTool(), QueryProfileTool()],
            model,
            model_parameters,
        )
