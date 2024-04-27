from typing import Optional, Dict, Any

from aita.agent.base import AitaAgent
from aita.tool.ipython import IPythonTool


class PythonAgent(AitaAgent):
    prompt_context = """
    script context: {script_context}
    """

    def __init__(self,
                 script_context: Optional[Dict[str, Any]],
                 model_id: str,
                 model_parameters: Optional[Dict] = None):
        if script_context:
            self.prompt_context = self.prompt_context.format(script_context=script_context)
        super().__init__(model_id,
                         model_parameters,
                         [IPythonTool(script_context=script_context)],
                         self.prompt_context)
