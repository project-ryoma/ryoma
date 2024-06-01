from typing import Dict
from aita.agent.base import ToolAgent
from aita.tool.sql import ConvertToArrowTool
from aita.tool.python import PythonTool
from aita.tool.pyarrow import ArrowTool
from pyarrow import Table


class PyArrowAgent(ToolAgent):
    def __init__(self, model: str, model_parameters: Dict = None):
        super().__init__([
            ConvertToArrowTool(),
            ArrowTool()
        ], model, model_parameters)

    def add_table(self, table: Table):
        self._fill_prompt_context(str(table.schema))
        for tool in self.tools:
            if isinstance(tool, PythonTool):
                tool.update_script_context(script_context=table)
        return self
