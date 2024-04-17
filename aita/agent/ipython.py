from aita.agent.base import AitaAgent
from aita.tool.ipython import IPythonTool


class PythonAgent(AitaAgent):
    def __init__(self, script_context, model, temperature):
        super().__init__(model, temperature, [IPythonTool(script_context=script_context)])
