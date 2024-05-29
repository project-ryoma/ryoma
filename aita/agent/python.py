from typing import Any, Dict, Optional

from aita.agent.base import ToolAgent
from aita.tool.ipython import PythonTool


class PythonAgent(ToolAgent):
    prompt_context = """
    script context: {script_context}
    """

    def __init__(
        self,
        script_context: Optional[Dict[str, Any]],
        model: str,
        model_parameters: Optional[Dict] = None,
    ):
        if script_context:
            self.prompt_context = self.prompt_context.format(script_context=script_context)
        super().__init__(
            [PythonTool(script_context=script_context)],
            model,
            model_parameters,
            self.prompt_context,
        )
