from typing import Dict, Optional

from aita.agent.base import ToolAgent
from aita.tool.python import PythonTool


class PythonAgent(ToolAgent):
    def __init__(
        self,
        model: str,
        model_parameters: Optional[Dict] = None,
    ):
        super().__init__([PythonTool()], model, model_parameters)

    def add_script_context(self, script_context):
        for tool in self.tools:
            tool.update_script_context(script_context=script_context)
        return self
